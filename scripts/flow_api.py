#!/usr/bin/env python3
"""
Flow API CLI helper for Claude Code skill integration.

Usage:
    python scripts/flow_api.py <command> [options]

Authentication:
    Set FLOW_REFRESH_TOKEN, FLOW_ORG, and FLOW_PROJECT environment variables.
    See .env.example for details.

Commands:
    auth                          Exchange refresh token and report validity
    req list                      List requirements (paginated)
    req get <id>                  Get full detail of a requirement
    req create <json>             Create requirement(s) from JSON
    req update <id> <json>        Update a requirement
    link req-req <id> <type> <target-id>  Link requirement to requirement
    link req-tc <req-id> <tc-id>  Link requirement to test case
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

BASE_URL = "https://api.flowengineering.com/rest/v1"


def load_dotenv():
    """Load .env from the repo root (two levels up from this script) if it exists."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, "..", ".env")
    env_path = os.path.normpath(env_path)
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Strip optional 'export ' prefix
            if line.startswith("export "):
                line = line[7:]
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


load_dotenv()

_access_token_cache = None


def get_refresh_token():
    token = os.environ.get("FLOW_REFRESH_TOKEN")
    if not token:
        print("ERROR: FLOW_REFRESH_TOKEN environment variable is not set.", file=sys.stderr)
        print("See .env.example for setup instructions.", file=sys.stderr)
        sys.exit(1)
    return token


def get_access_token():
    global _access_token_cache
    if _access_token_cache:
        return _access_token_cache

    refresh_token = get_refresh_token()
    data = json.dumps({"refreshToken": refresh_token}).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/auth/exchange",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read())
            _access_token_cache = body["accessToken"]
            return _access_token_cache
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"ERROR: Token exchange failed ({e.code}): {error_body}", file=sys.stderr)
        sys.exit(1)


def get_org_and_project(args):
    org = getattr(args, "org", None) or os.environ.get("FLOW_ORG")
    project = getattr(args, "project", None) or os.environ.get("FLOW_PROJECT")
    if not org:
        print("ERROR: Organisation alias required. Set FLOW_ORG or use --org.", file=sys.stderr)
        sys.exit(1)
    if not project:
        print("ERROR: Project alias required. Set FLOW_PROJECT or use --project.", file=sys.stderr)
        sys.exit(1)
    return org, project


def api_request(method, path, body=None):
    token = get_access_token()
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 204:
                return None
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"ERROR: API call failed ({e.code}) {method} {path}", file=sys.stderr)
        print(error_body, file=sys.stderr)
        sys.exit(1)


def cmd_auth(args):
    token = get_access_token()
    # Mask the token for safe display
    masked = token[:8] + "..." + token[-4:] if len(token) > 12 else "***"
    print(json.dumps({"status": "ok", "accessToken": masked}))


def cmd_req_list(args):
    org, project = get_org_and_project(args)
    path = f"/org/{org}/project/{project}/requirements/paged"
    params = []
    if args.limit:
        params.append(f"limit={args.limit}")
    if args.after:
        params.append(f"after={args.after}")
    if params:
        path += "?" + "&".join(params)
    result = api_request("GET", path)
    print(json.dumps(result, indent=2))


def cmd_req_get(args):
    org, project = get_org_and_project(args)
    path = f"/org/{org}/project/{project}/requirement/{args.id}"
    result = api_request("GET", path)
    print(json.dumps(result, indent=2))


def cmd_req_create(args):
    org, project = get_org_and_project(args)
    path = f"/org/{org}/project/{project}/requirements"
    try:
        body = json.loads(args.json_data)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    # Accept either a single object or an array
    if isinstance(body, dict):
        body = [body]
    result = api_request("POST", path, body)
    print(json.dumps(result, indent=2))


def cmd_req_update(args):
    org, project = get_org_and_project(args)
    path = f"/org/{org}/project/{project}/requirements"
    try:
        fields = json.loads(args.json_data)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    body = [{"requirementId": int(args.id), **fields}]
    result = api_request("PATCH", path, body)
    print(json.dumps(result, indent=2))


def cmd_link_req_req(args):
    org, project = get_org_and_project(args)
    link_type = args.link_type
    if link_type not in ("parent", "child", "cross"):
        print("ERROR: link_type must be one of: parent, child, cross", file=sys.stderr)
        sys.exit(1)
    path = f"/org/{org}/project/{project}/requirement/{args.req_id}/links/{link_type}"
    body = {"id": int(args.target_id)}
    if args.target_project:
        body["project"] = args.target_project
    result = api_request("POST", path, body)
    print(json.dumps(result, indent=2))


def cmd_link_req_tc(args):
    org, project = get_org_and_project(args)
    path = f"/org/{org}/project/{project}/link/requirementTestCase"
    body = {"links": [{"requirementId": int(args.req_id), "testCaseId": int(args.tc_id)}]}
    result = api_request("PUT", path, body)
    print(json.dumps(result, indent=2))


def build_parser():
    parser = argparse.ArgumentParser(
        description="Flow API CLI helper for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    org_args = argparse.ArgumentParser(add_help=False)
    org_args.add_argument("--org", help="Organisation alias (overrides FLOW_ORG)")
    org_args.add_argument("--project", help="Project alias (overrides FLOW_PROJECT)")

    sub = parser.add_subparsers(dest="command", required=True)

    # auth
    sub.add_parser("auth", help="Test credentials and report token validity")

    # req
    req_parser = sub.add_parser("req", help="Requirement operations")
    req_sub = req_parser.add_subparsers(dest="req_command", required=True)

    p_list = req_sub.add_parser("list", parents=[org_args], help="List requirements")
    p_list.add_argument("--limit", type=int, default=50, help="Max results (default 50)")
    p_list.add_argument("--after", help="Pagination cursor")

    p_get = req_sub.add_parser("get", parents=[org_args], help="Get a requirement by ID")
    p_get.add_argument("id", help="Requirement ID")

    p_create = req_sub.add_parser("create", parents=[org_args], help="Create requirement(s)")
    p_create.add_argument(
        "json_data",
        metavar="json",
        help='JSON object or array, e.g. \'{"name": "REQ-001", "description": "..."}\'',
    )

    p_update = req_sub.add_parser("update", parents=[org_args], help="Update a requirement")
    p_update.add_argument("id", help="Requirement ID")
    p_update.add_argument(
        "json_data",
        metavar="json",
        help='JSON fields to update, e.g. \'{"name": "New name"}\'',
    )

    # link
    link_parser = sub.add_parser("link", help="Traceability link operations")
    link_sub = link_parser.add_subparsers(dest="link_command", required=True)

    p_rr = link_sub.add_parser("req-req", parents=[org_args], help="Link requirement to requirement")
    p_rr.add_argument("req_id", help="Source requirement ID")
    p_rr.add_argument("link_type", choices=["parent", "child", "cross"], help="Link type")
    p_rr.add_argument("target_id", help="Target requirement ID")
    p_rr.add_argument("--target-project", help="Target project alias (for cross-project links)")

    p_rt = link_sub.add_parser("req-tc", parents=[org_args], help="Link requirement to test case")
    p_rt.add_argument("req_id", help="Requirement ID")
    p_rt.add_argument("tc_id", help="Test case ID")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "auth":
        cmd_auth(args)
    elif args.command == "req":
        if args.req_command == "list":
            cmd_req_list(args)
        elif args.req_command == "get":
            cmd_req_get(args)
        elif args.req_command == "create":
            cmd_req_create(args)
        elif args.req_command == "update":
            cmd_req_update(args)
    elif args.command == "link":
        if args.link_command == "req-req":
            cmd_link_req_req(args)
        elif args.link_command == "req-tc":
            cmd_link_req_tc(args)


if __name__ == "__main__":
    main()
