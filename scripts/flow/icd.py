"""ICD (Interface Control Document) extraction and generation.

Usage (via flow_cli.py):
    flow icd list
    flow icd generate [--pair "SystemA-SystemB"]
"""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime

_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUTPUTS_DIR = os.path.join(_REPO_ROOT, "outputs")


def run_icd(args):
    """Main ICD entrypoint."""
    from flow import client

    client.load_dotenv()
    org, project = client.get_org_and_project(args)
    subcmd = args.icd_command

    if subcmd == "list":
        _icd_list(client, org, project)
    elif subcmd == "generate":
        pair = getattr(args, "pair", None)
        _icd_generate(client, org, project, pair)
    else:
        print(f"ERROR: Unknown icd subcommand: {subcmd}", file=sys.stderr)
        sys.exit(1)


def _get_interface_pair(req):
    """Extract interface_pair custom field from a requirement, if present."""
    # The field may be stored in customFields dict or as a top-level field
    custom = req.get("customFields") or {}
    return custom.get("interface_pair") or req.get("interface_pair")


def _icd_list(client, org, project):
    """List all detected interface pairs."""
    reqs = client.api_request_all_pages(f"/org/{org}/project/{project}/requirements/paged")

    pairs = defaultdict(list)
    for r in reqs:
        pair = _get_interface_pair(r)
        if pair:
            pairs[pair].append(r)

    # Also detect pairs from requirements allocated to multiple systems (via system allocations)
    # This requires fetching system info - include any req with interface_pair field
    if not pairs:
        print("\nNo interface pairs detected.")
        print("Tag requirements with custom field 'interface_pair: SystemA-SystemB' to define ICD scope.")
        return

    print(f"\nDetected interface pairs ({len(pairs)}):\n")
    print(f"{'Interface Pair':<40}  {'Requirements':>14}")
    print("-" * 60)
    for pair_name, pair_reqs in sorted(pairs.items()):
        print(f"{pair_name:<40}  {len(pair_reqs):>14}")


def _icd_generate(client, org, project, pair_filter=None):
    """Generate a markdown ICD document."""
    reqs = client.api_request_all_pages(f"/org/{org}/project/{project}/requirements/paged")
    systems_result = client.api_request("GET", f"/org/{org}/project/{project}/systems")
    systems = systems_result if isinstance(systems_result, list) else (systems_result or {}).get("items", [])
    sys_name_by_id = {str(s.get("systemId") or s.get("id")): s.get("name", "Unknown") for s in systems}

    # Group by interface_pair
    pairs = defaultdict(list)
    for r in reqs:
        pair = _get_interface_pair(r)
        if pair:
            pairs[pair].append(r)

    if not pairs:
        print("No interface pairs found. Tag requirements with 'interface_pair' custom field.")
        return

    target_pairs = [pair_filter] if pair_filter else list(pairs.keys())

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    for pair_name in target_pairs:
        if pair_name not in pairs:
            print(f"WARNING: Pair '{pair_name}' not found.", file=sys.stderr)
            continue
        pair_reqs = pairs[pair_name]
        safe_name = pair_name.replace("/", "-").replace(" ", "_")
        out_path = os.path.join(OUTPUTS_DIR, f"icd_{safe_name}_{datetime.now().strftime('%Y%m%d')}.md")

        with open(out_path, "w") as f:
            f.write(f"# Interface Control Document: {pair_name}\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d')}  |  Project: {project}\n\n")

            f.write("## Interface summary\n\n")
            f.write("| Interface | Direction | Protocol/Medium | Status |\n")
            f.write("|-----------|-----------|-----------------|--------|\n")
            f.write(f"| {pair_name} | TBD | TBD | Active |\n\n")

            f.write("## Interface requirements\n\n")
            f.write("| Req ID | Statement | Verification Method | Owner | Stage |\n")
            f.write("|--------|-----------|---------------------|-------|-------|\n")
            for r in pair_reqs:
                rid = r.get("requirementId") or r.get("id")
                stmt = (r.get("description", "") or "").replace("|", "/")[:80]
                vm = r.get("verificationMethod", "TBD")
                owner = r.get("owner", "TBD")
                stage = r.get("stage", "TBD")
                f.write(f"| {rid} | {stmt} | {vm} | {owner} | {stage} |\n")

            f.write("\n## Design values\n\n")
            has_values = False
            for r in pair_reqs:
                custom = r.get("customFields") or {}
                if custom.get("value_source"):
                    has_values = True
                    rid = r.get("requirementId") or r.get("id")
                    f.write(f"- REQ {rid}: {r.get('name', '')} (source: {custom['value_source']})\n")
            if not has_values:
                f.write("_No model-derived design values identified for this interface._\n")

            f.write("\n## Open items\n\n")
            open_items = [r for r in pair_reqs if r.get("stage") in ("draft", None, "") or not r.get("verificationMethod")]
            if open_items:
                f.write("| Req ID | Name | Issue |\n")
                f.write("|--------|------|-------|\n")
                for r in open_items:
                    rid = r.get("requirementId") or r.get("id")
                    issue = "Draft stage" if r.get("stage") in ("draft", None, "") else "No verification method"
                    f.write(f"| {rid} | {r.get('name','')[:50]} | {issue} |\n")
            else:
                f.write("_No open items._\n")

        print(f"ICD generated: {out_path}")
