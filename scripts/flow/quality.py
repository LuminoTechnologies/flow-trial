"""Requirements quality review using configurable rules (INCOSE + custom).

Usage (via flow_cli.py):
    flow quality [--id <req-id>] [--fix-hints] [--output json]
"""

import json
import os
import re
import sys
from datetime import datetime

_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUTPUTS_DIR = os.path.join(_REPO_ROOT, "outputs")
DEFAULT_RULES_PATH = os.path.join(_REPO_ROOT, "config", "quality_rules.yaml")

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


def load_rules(rules_path=None):
    """Load rules from YAML. Falls back to built-in INCOSE defaults if YAML unavailable."""
    path = rules_path or DEFAULT_RULES_PATH
    if os.path.exists(path):
        try:
            import yaml
            with open(path) as f:
                data = yaml.safe_load(f)
            return data.get("rules", []) + data.get("custom", [])
        except ImportError:
            pass
    return _builtin_rules()


def _builtin_rules():
    return [
        {
            "id": "INC001",
            "name": "Statement must contain 'shall'",
            "severity": "error",
            "check": "regex_must_match",
            "pattern": r"\bshall\b",
            "field": "description",
            "fix_hint": "Rewrite the statement using 'shall' to express a mandatory requirement.",
        },
        {
            "id": "INC002",
            "name": "Avoid 'should', 'will', 'must' in statement",
            "severity": "warning",
            "check": "regex_must_not_match",
            "pattern": r"\b(should|will|must)\b",
            "field": "description",
            "fix_hint": "Replace with 'shall'. 'Should' implies optional; 'will' and 'must' are ambiguous.",
        },
        {
            "id": "INC003",
            "name": "No ambiguous terms",
            "severity": "warning",
            "check": "keyword_forbidden",
            "keywords": ["appropriate", "adequate", "as necessary", "as required", "sufficient", "satisfactory", "flexible", "easy"],
            "field": "description",
            "fix_hint": "Replace ambiguous terms with specific, measurable criteria.",
        },
        {
            "id": "INC004",
            "name": "Avoid compound requirements ('and'/'or' in shall clause)",
            "severity": "error",
            "check": "regex_must_not_match",
            "pattern": r"\bshall\b.*\b(and|or)\b.*\bshall\b",
            "field": "description",
            "fix_hint": "Split into separate requirements, one per 'shall' statement.",
        },
        {
            "id": "INC005",
            "name": "Owner field must be set",
            "severity": "warning",
            "check": "field_must_be_set",
            "field": "owner",
            "fix_hint": "Assign an owner to this requirement.",
        },
        {
            "id": "INC006",
            "name": "Verification method must be set",
            "severity": "warning",
            "check": "field_must_be_set",
            "field": "verificationMethod",
            "fix_hint": "Assign a verification method: Test, Analysis, Inspection, or Demonstration.",
        },
        {
            "id": "INC007",
            "name": "Requirement must be allocated to at least one system",
            "severity": "warning",
            "check": "field_must_be_set",
            "field": "systemId",
            "fix_hint": "Allocate this requirement to a system via the traceability panel.",
        },
        {
            "id": "INC008",
            "name": "Statement should reference a measurable quantity or condition",
            "severity": "info",
            "check": "regex_must_match",
            "pattern": r"\d+|within|less than|greater than|minimum|maximum|at least|at most|between",
            "field": "description",
            "fix_hint": "Add specific, measurable criteria (numbers, limits, conditions).",
        },
    ]


def check_requirement(req, rules):
    """Return a list of violations for a single requirement dict."""
    violations = []
    req_id = req.get("requirementId") or req.get("id", "?")
    req_name = req.get("name", "")
    for rule in rules:
        field = rule.get("field", "description")
        value = str(req.get(field, "") or "").strip()
        check = rule["check"]
        violated = False

        if check == "regex_must_match":
            if not re.search(rule["pattern"], value, re.IGNORECASE):
                violated = True
        elif check == "regex_must_not_match":
            if re.search(rule["pattern"], value, re.IGNORECASE):
                violated = True
        elif check == "keyword_forbidden":
            for kw in rule.get("keywords", []):
                if kw.lower() in value.lower():
                    violated = True
                    break
        elif check == "field_must_be_set":
            if not value or value in ("None", "null", ""):
                violated = True

        if violated:
            violations.append({
                "req_id": req_id,
                "req_name": req_name,
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "severity": rule["severity"],
                "fix_hint": rule.get("fix_hint", ""),
            })
    return violations


def run_quality(args):
    """Main quality review entrypoint."""
    from flow import client

    client.load_dotenv()
    org, project = client.get_org_and_project(args)

    rules_path = getattr(args, "rules", None)
    rules = load_rules(rules_path)
    fix_hints = getattr(args, "fix_hints", False)
    req_id = getattr(args, "id", None)

    print(f"Loading requirements...")
    if req_id:
        req = client.api_request("GET", f"/org/{org}/project/{project}/requirement/{req_id}")
        reqs = [req] if req else []
    else:
        reqs = client.api_request_all_pages(f"/org/{org}/project/{project}/requirements/paged")

    print(f"  Checking {len(reqs)} requirements against {len(rules)} rules...")

    all_violations = []
    for req in reqs:
        violations = check_requirement(req, rules)
        all_violations.extend(violations)

    # Group by severity
    by_severity = {"error": [], "warning": [], "info": []}
    for v in all_violations:
        by_severity.setdefault(v["severity"], []).append(v)

    # Print grouped results
    total = len(all_violations)
    for severity in ["error", "warning", "info"]:
        items = by_severity[severity]
        if not items:
            continue
        print(f"\n--- {severity.upper()} ({len(items)}) ---")
        print(f"{'Req ID':>8}  {'Rule':>8}  {'Requirement Name':<40}  {'Issue'}")
        print("-" * 100)
        for v in items:
            print(f"{str(v['req_id']):>8}  {v['rule_id']:>8}  {v['req_name'][:40]:<40}  {v['rule_name']}")
            if fix_hints and v["fix_hint"]:
                print(f"{'':>8}  {'':>8}  {'FIX:':<40}  {v['fix_hint']}")

    if total == 0:
        print("\nNo quality issues found.")
    else:
        errors = len(by_severity["error"])
        warnings = len(by_severity["warning"])
        infos = len(by_severity["info"])
        print(f"\nSummary: {errors} errors, {warnings} warnings, {infos} info  (across {len(reqs)} requirements)")

    # Write output report
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUTS_DIR, f"quality_{datetime.now().strftime('%Y%m%d')}.json")
    with open(out_path, "w") as f:
        json.dump({"requirements_checked": len(reqs), "violations": all_violations}, f, indent=2)
    print(f"Report saved: {out_path}")
