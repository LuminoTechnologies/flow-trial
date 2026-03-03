#!/usr/bin/env python3
"""
flow_cli.py - Flow API professional CLI

Usage:
    python scripts/flow_cli.py <command> [subcommand] [options]

Commands:
    auth                          Test credentials
    req list|get|create|update    Requirement CRUD
    link req-req|req-tc           Traceability links
    backup list                   List available backups
    restore <backup-id>           Restore from backup
    import <file.xlsx>            Import requirements from spreadsheet
    quality                       Requirements quality review (INCOSE rules)
    testgen                       Generate draft test cases
    trace systems|gaps|matrix|allocate|suggest  Traceability analysis
    impact req|system|diff        Change impact analysis
    icd list|generate             Interface Control Document generation
    models list|sync              Design values model awareness
"""

import argparse
import json
import os
import sys

# Allow 'from flow import ...' when running from scripts/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _add_org_args(parser):
    parser.add_argument("--org", help="Organisation alias (overrides FLOW_ORG)")
    parser.add_argument("--project", help="Project alias (overrides FLOW_PROJECT)")
    return parser


def build_parser():
    parser = argparse.ArgumentParser(
        prog="flow",
        description="Flow API professional CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- auth ---
    sub.add_parser("auth", help="Test credentials and report token validity")

    # --- req ---
    req_p = sub.add_parser("req", help="Requirement operations")
    req_sub = req_p.add_subparsers(dest="req_command", required=True)

    p = _add_org_args(req_sub.add_parser("list", help="List requirements"))
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--after", help="Pagination cursor")
    p.add_argument("--all", action="store_true", help="Fetch all pages")

    p = _add_org_args(req_sub.add_parser("get", help="Get a requirement by ID"))
    p.add_argument("id")

    p = _add_org_args(req_sub.add_parser("create", help="Create requirement(s)"))
    p.add_argument("json_data", metavar="json")

    p = _add_org_args(req_sub.add_parser("update", help="Update a requirement"))
    p.add_argument("id")
    p.add_argument("json_data", metavar="json")

    # --- link ---
    link_p = sub.add_parser("link", help="Traceability link operations")
    link_sub = link_p.add_subparsers(dest="link_command", required=True)

    p = _add_org_args(link_sub.add_parser("req-req", help="Link requirement to requirement"))
    p.add_argument("req_id")
    p.add_argument("link_type", choices=["parent", "child", "cross"])
    p.add_argument("target_id")
    p.add_argument("--target-project")

    p = _add_org_args(link_sub.add_parser("req-tc", help="Link requirement to test case"))
    p.add_argument("req_id")
    p.add_argument("tc_id")

    # --- backup ---
    backup_p = sub.add_parser("backup", help="Backup operations")
    backup_sub = backup_p.add_subparsers(dest="backup_command", required=True)
    backup_sub.add_parser("list", help="List available backups")

    # --- restore ---
    p = sub.add_parser("restore", help="Restore from a backup")
    _add_org_args(p)
    p.add_argument("backup_id", help="Backup ID to restore")

    # --- import ---
    p = _add_org_args(sub.add_parser("import", help="Import requirements from Excel"))
    p.add_argument("file", help="Path to .xlsx file")
    p.add_argument("--config", help="Path to import_config.yaml")
    p.add_argument("--preview", action="store_true", help="Parse only, no API calls")
    p.add_argument("--dry-run", dest="dry_run", action="store_true", help="Preview + quality check, no API calls")

    # --- quality ---
    p = _add_org_args(sub.add_parser("quality", help="Requirements quality review"))
    p.add_argument("--id", help="Review a single requirement by ID")
    p.add_argument("--fix-hints", dest="fix_hints", action="store_true")
    p.add_argument("--rules", help="Path to custom quality_rules.yaml")

    # --- testgen ---
    p = _add_org_args(sub.add_parser("testgen", help="Generate test cases from requirements"))
    p.add_argument("--id", help="Generate for a single requirement")
    p.add_argument("--commit", action="store_true", help="Create draft test cases in Flow")

    # --- trace ---
    trace_p = _add_org_args(sub.add_parser("trace", help="Traceability analysis"))
    trace_sub = trace_p.add_subparsers(dest="trace_command", required=True)
    trace_sub.add_parser("systems", help="List systems and requirement counts")
    trace_sub.add_parser("gaps", help="List unallocated requirements")
    p = trace_sub.add_parser("matrix", help="Generate traceability matrix")
    p.add_argument("--format", choices=["csv", "markdown"], default="markdown")
    p = _add_org_args(trace_sub.add_parser("allocate", help="Allocate requirement to system"))
    p.add_argument("req_id")
    p.add_argument("system_id")
    trace_sub.add_parser("suggest", help="Suggest system allocations for unallocated requirements")

    # --- impact ---
    impact_p = _add_org_args(sub.add_parser("impact", help="Change impact analysis"))
    impact_sub = impact_p.add_subparsers(dest="impact_command", required=True)
    p = impact_sub.add_parser("req", help="Impact of changing a requirement")
    p.add_argument("id")
    p = impact_sub.add_parser("system", help="Impact of changing a system")
    p.add_argument("id")
    p = impact_sub.add_parser("diff", help="Diff current state against a backup")
    p.add_argument("backup_id")

    # --- icd ---
    icd_p = _add_org_args(sub.add_parser("icd", help="Interface Control Document operations"))
    icd_sub = icd_p.add_subparsers(dest="icd_command", required=True)
    icd_sub.add_parser("list", help="List detected interface pairs")
    p = icd_sub.add_parser("generate", help="Generate ICD document(s)")
    p.add_argument("--pair", help="Interface pair name, e.g. 'SystemA-SystemB'")

    # --- models ---
    models_p = _add_org_args(sub.add_parser("models", help="Design values model awareness"))
    models_sub = models_p.add_subparsers(dest="models_command", required=True)
    models_sub.add_parser("list", help="List requirements with numeric values")
    p = models_sub.add_parser("sync", help="Sync numeric values from model CSV export")
    p.add_argument("--csv", required=True, help="Path to CSV file from model")

    return parser


def main():
    from flow import client, backup as backup_module

    client.load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    cmd = args.command

    if cmd == "auth":
        token = client.get_access_token()
        masked = token[:8] + "..." + token[-4:] if len(token) > 12 else "***"
        print(json.dumps({"status": "ok", "accessToken": masked}))

    elif cmd == "req":
        org, project = client.get_org_and_project(args)
        if args.req_command == "list":
            if getattr(args, "all", False):
                items = client.api_request_all_pages(f"/org/{org}/project/{project}/requirements/paged")
                print(json.dumps(items, indent=2))
            else:
                path = f"/org/{org}/project/{project}/requirements/paged?limit={args.limit}"
                if args.after:
                    path += f"&after={args.after}"
                print(json.dumps(client.api_request("GET", path), indent=2))
        elif args.req_command == "get":
            print(json.dumps(client.api_request("GET", f"/org/{org}/project/{project}/requirement/{args.id}"), indent=2))
        elif args.req_command == "create":
            body = json.loads(args.json_data)
            if isinstance(body, dict):
                body = [body]
            print(json.dumps(client.api_request("POST", f"/org/{org}/project/{project}/requirements", body), indent=2))
        elif args.req_command == "update":
            fields = json.loads(args.json_data)
            body = [{"requirementId": int(args.id), **fields}]
            print(json.dumps(client.api_request("PATCH", f"/org/{org}/project/{project}/requirements", body), indent=2))

    elif cmd == "link":
        org, project = client.get_org_and_project(args)
        if args.link_command == "req-req":
            path = f"/org/{org}/project/{project}/requirement/{args.req_id}/links/{args.link_type}"
            body = {"id": int(args.target_id)}
            if args.target_project:
                body["project"] = args.target_project
            print(json.dumps(client.api_request("POST", path, body), indent=2))
        elif args.link_command == "req-tc":
            path = f"/org/{org}/project/{project}/link/requirementTestCase"
            body = {"links": [{"requirementId": int(args.req_id), "testCaseId": int(args.tc_id)}]}
            print(json.dumps(client.api_request("PUT", path, body), indent=2))

    elif cmd == "backup":
        if args.backup_command == "list":
            backups = backup_module.list_backups()
            if not backups:
                print("No backups found.")
            else:
                print(f"{'Backup ID':<50}")
                print("-" * 50)
                for b in backups:
                    print(b)

    elif cmd == "restore":
        org, project = client.get_org_and_project(args)
        snapshot, manifest = backup_module.load_backup(args.backup_id)
        if manifest:
            print(f"Manifest: {json.dumps(manifest, indent=2)}")
        reqs = snapshot if isinstance(snapshot, list) else []
        print(f"Restoring {len(reqs)} requirements from backup '{args.backup_id}'...")
        if not reqs:
            print("Nothing to restore.")
            return
        path = f"/org/{org}/project/{project}/requirements"
        for r in reqs:
            rid = r.get("requirementId") or r.get("id")
            if not rid:
                continue
            fields = {k: v for k, v in r.items() if k not in ("requirementId", "id", "createdAt", "updatedAt")}
            body = [{"requirementId": int(rid), **fields}]
            client.api_request("PATCH", path, body)
            print(f"  Restored REQ {rid}")
        print("Restore complete.")

    elif cmd == "import":
        from flow.importer import run_import
        run_import(args)

    elif cmd == "quality":
        from flow.quality import run_quality
        run_quality(args)

    elif cmd == "testgen":
        from flow.testgen import run_testgen
        run_testgen(args)

    elif cmd == "trace":
        from flow.traceability import run_trace
        run_trace(args)

    elif cmd == "impact":
        from flow.impact import run_impact
        run_impact(args)

    elif cmd == "icd":
        from flow.icd import run_icd
        run_icd(args)

    elif cmd == "models":
        from flow.models import run_models
        run_models(args)


if __name__ == "__main__":
    main()
