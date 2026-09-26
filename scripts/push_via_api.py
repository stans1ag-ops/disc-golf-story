"""Commit local story-site changes to GitHub via the Git Data API.

Usage: python3 scripts/push_via_api.py "<commit message>" [glob-pattern ...]

Extra glob patterns (relative to repo root) may be passed to widen the commit
beyond the defaults. Commits every new/modified file matching the patterns,
building on the current main HEAD. No local git remote needed.
"""

import base64
import json
import sys
import time
import urllib.request
from http.client import RemoteDisconnected, HTTPException

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import (
    add_surrogate_to_request,
    read_json_response,
)

OWNER = "stans1ag-ops"
REPO_NAME = "disc-golf-story"
API = f"https://api.github.com/repos/{OWNER}/{REPO_NAME}"
HOSTS = ("api.github.com",)


def api(method, url, payload=None, retries=5):
    data = json.dumps(payload).encode() if payload is not None else None
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header("Accept", "application/vnd.github+json")
            if data:
                req.add_header("Content-Type", "application/json")
            add_surrogate_to_request(req, "custom.github", allowed_hosts=HOSTS)
            resp = urllib.request.urlopen(req, timeout=120)
            return read_json_response(resp)
        except (RemoteDisconnected, HTTPException, ConnectionError,
                TimeoutError, OSError) as e:
            last_err = e
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"API call failed after {retries} attempts: {last_err}")


def main():
    message = sys.argv[1] if len(sys.argv) > 1 else "Update story site"
    ref = api("GET", f"{API}/git/ref/heads/main")
    head_sha = ref["object"]["sha"]
    print("HEAD:", head_sha)

    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    files = []
    patterns = tuple(sys.argv[2:]) or ("tyson/**/*", "index.html", "scripts/build_tyson_site.py")
    for pattern in patterns:
        for p in root.glob(pattern):
            if p.is_file():
                files.append(p.relative_to(root).as_posix())
    files = sorted(set(files))
    print(f"{len(files)} files to commit")

    base_tree = api("GET", f"{API}/git/commits/{head_sha}")["tree"]["sha"]
    tree_items = []
    for rel in files:
        data = (root / rel).read_bytes()
        blob = api("POST", f"{API}/git/blobs",
                   {"content": base64.b64encode(data).decode(), "encoding": "base64"})
        tree_items.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        print("blob", rel, blob["sha"][:8])

    new_tree = api("POST", f"{API}/git/trees",
                   {"base_tree": base_tree, "tree": tree_items})["sha"]
    commit = api("POST", f"{API}/git/commits",
                 {"message": message, "tree": new_tree, "parents": [head_sha]})
    api("PATCH", f"{API}/git/refs/heads/main", {"sha": commit["sha"]})
    print("Committed:", commit["sha"])
    print("Pushed to main.")


if __name__ == "__main__":
    main()
