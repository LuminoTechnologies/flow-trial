"""Test case generation from requirements.

Generates structured test case drafts from requirement statements and writes them
to outputs/testcases_draft_YYYYMMDD.json for review.

Usage (via flow_cli.py):
    flow testgen [--id <req-id>] [--commit]
"""

import json
import os
import re
import sys
from datetime import datetime

_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUTPUTS_DIR = os.path.join(_REPO_ROOT, "outputs")


def _draft_test_case(req):
    """Generate a structured test case draft from a requirement dict."""
    req_id = req.get("requirementId") or req.get("id", "?")
    req_name = req.get("name", f"REQ-{req_id}")
    description = req.get("description", "")

    # Extract measurable criteria (numbers, limits) from description
    criteria = []
    if re.search(r"\d+", description):
        criteria.append("Verify the stated numerical value/limit is met.")
    if re.search(r"\b(within|less than|greater than|minimum|maximum|at least|at most|between)\b", description, re.IGNORECASE):
        criteria.append("Verify the stated boundary condition is satisfied.")
    if not criteria:
        criteria.append("Verify the requirement is satisfied by inspection or functional test.")

    return {
        "source_requirement_id": req_id,
        "source_requirement_name": req_name,
        "test_case_name": f"TC: {req_name}",
        "description": f"Verify that: {description}" if description else f"Verify requirement {req_name}.",
        "preconditions": "System is in its normal operational state.",
        "steps": [
            f"1. Set up the test environment for {req_name}.",
            "2. Execute the test procedure relevant to the requirement.",
        ] + [f"3. {c}" for c in criteria] + [
            "4. Record observations and compare to expected results.",
            "5. Document pass/fail outcome with supporting evidence.",
        ],
        "expected_result": f"The system satisfies: {description}" if description else f"Requirement {req_name} is satisfied.",
        "verification_method": req.get("verificationMethod", "Test"),
        "stage": "draft",
        "custom_fields": {"source": "auto-generated"},
    }


def run_testgen(args):
    """Main test generation entrypoint."""
    from flow import client, backup

    client.load_dotenv()
    org, project = client.get_org_and_project(args)

    req_id = getattr(args, "id", None)
    commit = getattr(args, "commit", False)

    draft_files = [f for f in os.listdir(OUTPUTS_DIR) if f.startswith("testcases_draft_")] if os.path.exists(OUTPUTS_DIR) else []

    if commit:
        # Commit mode: read draft file and create test cases in Flow
        if not draft_files:
            print("ERROR: No draft test cases found. Run 'flow testgen' first.", file=sys.stderr)
            sys.exit(1)
        draft_path = os.path.join(OUTPUTS_DIR, sorted(draft_files)[-1])
        print(f"Reading draft: {draft_path}")
        with open(draft_path) as f:
            drafts = json.load(f)

        print(f"Creating {len(drafts)} test cases in Flow...")
        tc_path = f"/org/{org}/project/{project}/testCases"
        created = []
        for draft in drafts:
            # Build test case body (simplified to fields the API accepts)
            body = [{
                "name": draft["test_case_name"],
                "description": draft["description"],
                "notes": f"Auto-generated from requirement {draft['source_requirement_id']}\n\nSteps:\n" + "\n".join(draft["steps"]),
            }]
            result = client.api_request("POST", tc_path, body)
            if result:
                tc_ids = [r.get("testCaseId") or r.get("id") for r in (result if isinstance(result, list) else [result])]
                for tc_id in tc_ids:
                    if tc_id:
                        # Link test case to requirement
                        link_path = f"/org/{org}/project/{project}/link/requirementTestCase"
                        client.api_request("PUT", link_path, {"links": [{"requirementId": int(draft["source_requirement_id"]), "testCaseId": int(tc_id)}]})
                        created.append({"tc_id": tc_id, "req_id": draft["source_requirement_id"]})
                        print(f"  Created TC {tc_id} linked to REQ {draft['source_requirement_id']}")

        print(f"\nDone: {len(created)} test cases created and linked.")
        return

    # Draft mode: fetch requirements and generate test case stubs
    print("Fetching requirements...")
    if req_id:
        req = client.api_request("GET", f"/org/{org}/project/{project}/requirement/{req_id}")
        reqs = [req] if req else []
    else:
        reqs = client.api_request_all_pages(f"/org/{org}/project/{project}/requirements/paged")

    # Only generate test cases for requirements that contain 'shall'
    eligible = [r for r in reqs if "shall" in str(r.get("description", "")).lower()]
    print(f"  {len(reqs)} requirements fetched, {len(eligible)} contain 'shall' (eligible for test generation).")

    drafts = [_draft_test_case(r) for r in eligible]

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUTS_DIR, f"testcases_draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(out_path, "w") as f:
        json.dump(drafts, f, indent=2)

    print(f"\n{len(drafts)} draft test cases written to: {out_path}")
    print("Review the file, edit as needed, then run 'flow testgen --commit' to create them in Flow.")
