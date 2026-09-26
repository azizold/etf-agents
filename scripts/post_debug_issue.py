"""Posts a captured log tail as a GitHub Issue — used by the workflows to
surface a failure's traceback somewhere readable from outside the Actions
log viewer (whose storage isn't reachable from every environment).

Usage: python scripts/post_debug_issue.py <title> <log_file_path>
"""
import json
import os
import sys
import urllib.request

title = sys.argv[1]
log_path = sys.argv[2]

with open(log_path, "r", errors="replace") as f:
    tail = f.read()[-60000:]

body = f"```\n{tail}\n```"
repo = os.environ["GITHUB_REPOSITORY"]
token = os.environ["GITHUB_TOKEN"]

req = urllib.request.Request(
    f"https://api.github.com/repos/{repo}/issues",
    data=json.dumps({"title": title, "body": body, "labels": ["debug"]}).encode(),
    headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    },
    method="POST",
)
with urllib.request.urlopen(req) as resp:
    print(resp.read().decode())
