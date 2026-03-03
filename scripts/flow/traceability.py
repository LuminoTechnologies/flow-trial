"""Traceability analysis: system allocation, gap detection, traceability matrix.

Usage (via flow_cli.py):
    flow trace systems
    flow trace gaps
    flow trace matrix [--format csv|markdown]
    flow trace allocate <req-id> <system-id>
    flow trace suggest
"""

import csv
import json
import os
import sys
from datetime import datetime
from io import StringIO

_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUTPUTS_DIR = os.path.join(_REPO_ROOT, "outputs")


def _fetch_systems(client, org, project):
    result = client.api_request("GET", f"/org/{org}/project/{project}/systems")
    if isinstance(result, list):
        return result
    return result.get("items", result.get("systems", [])) if result else []


def _fetch_all_reqs(client, org, project):
    return client.api_request_all_pages(f"/org/{org}/project/{project}/requirements/paged")


def run_trace(args):
    """Main traceability entrypoint - routes to subcommand."""
    from flow import client, backup

    client.load_dotenv()
    org, project = client.get_org_and_project(args)
    subcmd = args.trace_command

    if subcmd == "systems":
        _trace_systems(client, org, project)
    elif subcmd == "gaps":
        _trace_gaps(client, org, project)
    elif subcmd == "matrix":
        fmt = getattr(args, "format", "markdown")
        _trace_matrix(client, org, project, fmt)
    elif subcmd == "allocate":
        _trace_allocate(client, org, project, args.req_id, args.system_id, backup)
    elif subcmd == "suggest":
        _trace_suggest(client, org, project)
    else:
        print(f"ERROR: Unknown trace subcommand: {subcmd}", file=sys.stderr)
        sys.exit(1)


def _trace_systems(client, org, project):
    systems = _fetch_systems(client, org, project)
    reqs = _fetch_all_reqs(client, org, project)

    # Group reqs by system
    system_reqs = {s.get("systemId") or s.get("id"): [] for s in systems}
    for r in reqs:
        sys_id = r.get("systemId")
        if sys_id and sys_id in system_reqs:
            system_reqs[sys_id].append(r)

    print(f"\n{'System':<40} {'ID':>8}  {'Reqs':>6}")
    print("-" * 60)
    for s in systems:
        sys_id = s.get("systemId") or s.get("id")
        name = s.get("name", "")
        count = len(system_reqs.get(sys_id, []))
        print(f"{name:<40} {str(sys_id):>8}  {count:>6}")
    print(f"\nTotal: {len(systems)} systems, {len(reqs)} requirements")


def _trace_gaps(client, org, project):
    reqs = _fetch_all_reqs(client, org, project)
    unallocated = [r for r in reqs if not r.get("systemId")]
    print(f"\nRequirements not allocated to any system: {len(unallocated)}")
    if unallocated:
        print(f"\n{'Req ID':>8}  {'Name':<50}")
        print("-" * 62)
        for r in unallocated:
            req_id = r.get("requirementId") or r.get("id")
            print(f"{str(req_id):>8}  {r.get('name','')[:50]}")


def _trace_matrix(client, org, project, fmt="markdown"):
    systems = _fetch_systems(client, org, project)
    reqs = _fetch_all_reqs(client, org, project)

    sys_ids = [s.get("systemId") or s.get("id") for s in systems]
    sys_names = {s.get("systemId") or s.get("id"): s.get("name", str(s.get("id"))) for s in systems}

    # Build matrix rows
    matrix_rows = []
    for r in reqs:
        req_id = r.get("requirementId") or r.get("id")
        row = {"req_id": req_id, "name": r.get("name", ""), "systems": {}}
        allocated_sys = r.get("systemId")
        for sid in sys_ids:
            row["systems"][sid] = "X" if allocated_sys == sid else ""
        matrix_rows.append(row)

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if fmt == "csv":
        out_path = os.path.join(OUTPUTS_DIR, f"traceability_matrix_{timestamp}.csv")
        with open(out_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Req ID", "Name"] + [sys_names[sid] for sid in sys_ids])
            for row in matrix_rows:
                writer.writerow([row["req_id"], row["name"]] + [row["systems"][sid] for sid in sys_ids])
        print(f"Matrix (CSV): {out_path}")
    else:
        out_path = os.path.join(OUTPUTS_DIR, f"traceability_matrix_{timestamp}.md")
        with open(out_path, "w") as f:
            header = "| Req ID | Name | " + " | ".join(sys_names[sid] for sid in sys_ids) + " |"
            sep = "|--------|------|" + "|".join(["---"] * len(sys_ids)) + "|"
            f.write(header + "\n" + sep + "\n")
            for row in matrix_rows:
                cells = [str(row["req_id"]), row["name"][:50]] + [row["systems"][sid] for sid in sys_ids]
                f.write("| " + " | ".join(cells) + " |\n")
        print(f"Matrix (Markdown): {out_path}")

    print(f"{len(matrix_rows)} requirements x {len(systems)} systems")


def _trace_allocate(client, org, project, req_id, system_id, backup_module):
    # Backup the current requirement before modifying
    req = client.api_request("GET", f"/org/{org}/project/{project}/requirement/{req_id}")
    backup_module.create_backup("trace-allocate", [req], manifest={"req_id": req_id, "system_id": system_id})

    body = [{"requirementId": int(req_id), "systemId": int(system_id)}]
    result = client.api_request("PATCH", f"/org/{org}/project/{project}/requirements", body)
    print(json.dumps(result, indent=2))


def _trace_suggest(client, org, project):
    """Suggest system allocations for unallocated requirements (heuristic - for Claude review)."""
    systems = _fetch_systems(client, org, project)
    reqs = _fetch_all_reqs(client, org, project)
    unallocated = [r for r in reqs if not r.get("systemId")]

    if not unallocated:
        print("All requirements are already allocated to a system.")
        return

    sys_names = [(s.get("systemId") or s.get("id"), s.get("name", "")) for s in systems]

    print(f"\nSuggested allocations for {len(unallocated)} unallocated requirements:")
    print("(These are suggestions for review - use 'flow trace allocate' to commit them)\n")

    suggestions = []
    for r in unallocated:
        req_id = r.get("requirementId") or r.get("id")
        desc = (r.get("description", "") + " " + r.get("name", "")).lower()
        # Simple keyword-based heuristic: match system name words to requirement text
        best = None
        best_score = 0
        for sid, sname in sys_names:
            words = [w.lower() for w in sname.split() if len(w) > 3]
            score = sum(1 for w in words if w in desc)
            if score > best_score:
                best_score = score
                best = (sid, sname)
        suggestion = {"req_id": req_id, "req_name": r.get("name", ""), "suggested_system_id": best[0] if best else None, "suggested_system": best[1] if best else "unknown", "confidence": "low" if best_score == 0 else "medium"}
        suggestions.append(suggestion)
        print(f"  REQ {req_id}: {r.get('name','')[:50]}")
        print(f"    -> {suggestion['suggested_system']} (ID: {suggestion['suggested_system_id']}, confidence: {suggestion['confidence']})")

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUTS_DIR, f"trace_suggestions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(out_path, "w") as f:
        json.dump(suggestions, f, indent=2)
    print(f"\nSuggestions saved: {out_path}")
