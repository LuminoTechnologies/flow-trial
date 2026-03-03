"""Change impact analysis.

Usage (via flow_cli.py):
    flow impact req <id>
    flow impact system <id>
    flow impact diff <backup-id>
"""

import json
import os
import sys
from datetime import datetime

_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUTPUTS_DIR = os.path.join(_REPO_ROOT, "outputs")


def run_impact(args):
    """Main impact analysis entrypoint."""
    from flow import client, backup

    client.load_dotenv()
    subcmd = args.impact_command

    if subcmd == "req":
        org, project = client.get_org_and_project(args)
        _impact_req(client, org, project, args.id)
    elif subcmd == "system":
        org, project = client.get_org_and_project(args)
        _impact_system(client, org, project, args.id)
    elif subcmd == "diff":
        org, project = client.get_org_and_project(args)
        _impact_diff(client, org, project, args.backup_id, backup)
    else:
        print(f"ERROR: Unknown impact subcommand: {subcmd}", file=sys.stderr)
        sys.exit(1)


def _impact_req(client, org, project, req_id):
    """Show everything linked to a requirement."""
    print(f"\nImpact analysis for requirement {req_id}:")
    req = client.api_request("GET", f"/org/{org}/project/{project}/requirement/{req_id}")
    if not req:
        print(f"ERROR: Requirement {req_id} not found.", file=sys.stderr)
        return

    print(f"\n  Name: {req.get('name')}")
    print(f"  Description: {req.get('description', '')[:100]}")
    print(f"  System: {req.get('systemId', 'unallocated')}")
    print(f"  Owner: {req.get('owner', 'unset')}")
    print(f"  Stage: {req.get('stage', 'unknown')}")

    # Links
    links = req.get("links", {})
    parents = links.get("parent", [])
    children = links.get("child", [])
    cross = links.get("cross", [])

    if parents:
        print(f"\n  Parent requirements: {len(parents)}")
        for p in parents:
            print(f"    - REQ {p.get('id')}: {p.get('name', '')}")
    if children:
        print(f"\n  Child requirements: {len(children)}")
        for c in children:
            print(f"    - REQ {c.get('id')}: {c.get('name', '')}")
    if cross:
        print(f"\n  Cross-links: {len(cross)}")
        for x in cross:
            print(f"    - REQ {x.get('id')} (project: {x.get('project', 'same')})")

    # Test cases
    test_cases = req.get("testCases", [])
    if test_cases:
        print(f"\n  Linked test cases: {len(test_cases)}")
        for tc in test_cases:
            print(f"    - TC {tc.get('testCaseId') or tc.get('id')}: {tc.get('name', '')}")
    else:
        print("\n  Linked test cases: none")

    print(f"\n  Change impact summary:")
    total_impacted = len(parents) + len(children) + len(cross) + len(test_cases)
    print(f"    Changing this requirement may affect {total_impacted} linked items.")


def _impact_system(client, org, project, system_id):
    """Show all requirements, test cases, and linked systems for a system."""
    print(f"\nImpact analysis for system {system_id}:")
    system = client.api_request("GET", f"/org/{org}/project/{project}/system/{system_id}")
    if not system:
        print(f"ERROR: System {system_id} not found.", file=sys.stderr)
        return

    print(f"\n  Name: {system.get('name')}")

    # Requirements allocated to this system
    all_reqs = client.api_request_all_pages(f"/org/{org}/project/{project}/requirements/paged")
    sys_reqs = [r for r in all_reqs if r.get("systemId") == int(system_id)]
    print(f"\n  Requirements allocated: {len(sys_reqs)}")
    for r in sys_reqs[:20]:
        req_id = r.get("requirementId") or r.get("id")
        print(f"    - REQ {req_id}: {r.get('name','')[:60]}")
    if len(sys_reqs) > 20:
        print(f"    ... and {len(sys_reqs) - 20} more")

    print(f"\n  Change impact summary:")
    print(f"    This system has {len(sys_reqs)} allocated requirements. Changes to the system affect all of them.")


def _impact_diff(client, org, project, backup_id, backup_module):
    """Compare current state against a backup snapshot."""
    print(f"\nDiff: current state vs backup '{backup_id}'")
    snapshot, manifest = backup_module.load_backup(backup_id)

    print("Fetching current requirements...")
    current_reqs = client.api_request_all_pages(f"/org/{org}/project/{project}/requirements/paged")

    # Index by ID
    snap_by_id = {}
    for r in (snapshot if isinstance(snapshot, list) else []):
        rid = r.get("requirementId") or r.get("id")
        snap_by_id[rid] = r

    curr_by_id = {}
    for r in current_reqs:
        rid = r.get("requirementId") or r.get("id")
        curr_by_id[rid] = r

    added = [rid for rid in curr_by_id if rid not in snap_by_id]
    removed = [rid for rid in snap_by_id if rid not in curr_by_id]
    modified = []
    for rid in curr_by_id:
        if rid in snap_by_id:
            old = snap_by_id[rid]
            new = curr_by_id[rid]
            changes = {}
            for field in ("name", "description", "stage", "owner", "systemId"):
                if old.get(field) != new.get(field):
                    changes[field] = {"from": old.get(field), "to": new.get(field)}
            if changes:
                modified.append({"id": rid, "name": new.get("name"), "changes": changes})

    print(f"\n  Added:    {len(added)} requirements")
    for rid in added:
        r = curr_by_id[rid]
        print(f"    + REQ {rid}: {r.get('name','')[:60]}")

    print(f"\n  Removed:  {len(removed)} requirements")
    for rid in removed:
        r = snap_by_id[rid]
        print(f"    - REQ {rid}: {r.get('name','')[:60]}")

    print(f"\n  Modified: {len(modified)} requirements")
    for m in modified:
        print(f"    ~ REQ {m['id']}: {m['name'][:50]}")
        for field, delta in m["changes"].items():
            print(f"        {field}: {str(delta['from'])[:40]} -> {str(delta['to'])[:40]}")

    # Save diff report
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUTS_DIR, f"diff_{backup_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(out_path, "w") as f:
        json.dump({"backup_id": backup_id, "added": added, "removed": removed, "modified": modified}, f, indent=2)
    print(f"\nDiff report saved: {out_path}")
