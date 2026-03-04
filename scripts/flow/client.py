"""Flow API client: authentication, request helpers, and pagination."""

import json
import os
import sys
import urllib.request
import urllib.error

BASE_URL = "https://api.flowengineering.com/rest/v1"

_access_token_cache = None


def load_dotenv():
    """Load .env from the repo root if it exists."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.normpath(os.path.join(script_dir, "..", "..", ".env"))
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:]
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


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


def get_org_and_project(args=None):
    org = (getattr(args, "org", None) if args else None) or os.environ.get("FLOW_ORG")
    project = (getattr(args, "project", None) if args else None) or os.environ.get("FLOW_PROJECT")
    if not org:
        print("ERROR: Organisation alias required. Set FLOW_ORG or use --org.", file=sys.stderr)
        sys.exit(1)
    if not project:
        print("ERROR: Project alias required. Set FLOW_PROJECT or use --project.", file=sys.stderr)
        sys.exit(1)
    return org, project


def api_request(method, path, body=None):
    """Make a single API request. Returns parsed JSON or None for 204."""
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


def api_request_all_pages(path_template, limit=100):
    """Fetch all pages of a paged endpoint. path_template must contain a paged path.

    Returns a list of all items across all pages.
    """
    items = []
    after = None
    while True:
        path = path_template
        params = [f"limit={limit}"]
        if after:
            params.append(f"after={after}")
        path += "?" + "&".join(params)
        result = api_request("GET", path)
        if not result:
            break
        page_items = result.get("results", result.get("items", result.get("requirements", [])))
        items.extend(page_items)
        cursor = result.get("nextCursor") or result.get("after") or (result.get("cursor") if result.get("hasMore") else None)
        if not cursor or not page_items:
            break
        after = cursor
    return items
