"""Design values model awareness.

Usage (via flow_cli.py):
    flow models list
    flow models sync --csv <file>
"""

import csv
import json
import os
import sys
from datetime import datetime

_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUTPUTS_DIR = os.path.join(_REPO_ROOT, "outputs")


def run_models(args):
    """Main models entrypoint."""
    from flow import client, backup

    client.load_dotenv()
    org, project = client.get_org_and_project(args)
    subcmd = args.models_command

    if subcmd == "list":
        _models_list(client, org, project)
    elif subcmd == "sync":
        _models_sync(client, org, project, args.csv, backup)
    else:
        print(f"ERROR: Unknown models subcommand: {subcmd}", file=sys.stderr)
        sys.exit(1)


def _has_numeric_value(req):
    """Return True if the requirement description contains a numeric value."""
    import re
    desc = req.get("description", "") or ""
    return bool(re.search(r"\d+\.?\d*\s*[a-zA-Z%°]*", desc))


def _models_list(client, org, project):
    """List all requirements with numeric values, grouped by model source tag."""
    reqs = client.api_request_all_pages(f"/org/{org}/project/{project}/requirements/paged")

    numeric_reqs = [r for r in reqs if _has_numeric_value(r)]
    print(f"\nRequirements with numeric values: {len(numeric_reqs)} of {len(reqs)} total\n")

    # Group by value_source custom field
    by_source = {}
    no_source = []
    for r in numeric_reqs:
        custom = r.get("customFields") or {}
        source = custom.get("value_source") or r.get("value_source")
        if source:
            by_source.setdefault(source, []).append(r)
        else:
            no_source.append(r)

    for source, group in sorted(by_source.items()):
        print(f"  Source: {source} ({len(group)} requirements)")
        for r in group:
            rid = r.get("requirementId") or r.get("id")
            print(f"    REQ {rid}: {r.get('name','')[:60]}")

    if no_source:
        print(f"\n  WARNING: {len(no_source)} requirements have numeric values but no 'value_source' tag:")
        for r in no_source:
            rid = r.get("requirementId") or r.get("id")
            print(f"    REQ {rid}: {r.get('name','')[:60]}")
        print("\n  Consider tagging these with customField 'value_source: model' or 'value_source: manual'.")


def _models_sync(client, org, project, csv_path, backup_module):
    """Read a CSV export from a model and update matched requirements in Flow."""
    if not csv_path or not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    print(f"Read {len(csv_rows)} rows from {csv_path}")

    # Fetch all requirements
    reqs = client.api_request_all_pages(f"/org/{org}/project/{project}/requirements/paged")

    # Build lookup by import_id and name
    by_import_id = {}
    by_name = {}
    for r in reqs:
        notes = r.get("notes", "") or ""
        for line in notes.splitlines():
            if line.startswith("import_id:"):
                by_import_id[line.split(":", 1)[1].strip()] = r
        name = (r.get("name", "") or "").strip()
        if name:
            by_name[name.lower()] = r

    # Snapshot before updating
    updated_reqs = []
    updates = []
    for row in csv_rows:
        import_id = row.get("import_id", "").strip()
        name = row.get("name", "").strip()
        new_desc = row.get("description", "").strip() or row.get("value", "").strip()
        if not new_desc:
            continue

        req = by_import_id.get(import_id) or by_name.get(name.lower())
        if not req:
            print(f"  WARNING: No match found for import_id='{import_id}', name='{name}'. Skipping.")
            continue
        updated_reqs.append(req)
        updates.append((req, new_desc))

    if not updates:
        print("No matching requirements found to update.")
        return

    backup_module.create_backup("models-sync", updated_reqs, manifest={"csv": csv_path, "updates": len(updates)})

    patch_path = f"/org/{org}/project/{project}/requirements"
    for req, new_desc in updates:
        rid = req.get("requirementId") or req.get("id")
        body = [{"requirementId": int(rid), "description": new_desc}]
        result = client.api_request("PATCH", patch_path, body)
        print(f"  Updated REQ {rid}")

    print(f"\nSync complete: {len(updates)} requirements updated.")
