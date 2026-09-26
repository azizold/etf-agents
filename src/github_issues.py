"""Deck delivery channel: every deck becomes a GitHub Issue in this repo.

You get GitHub's own mobile/email notifications the moment a deck posts.
You respond by commenting on the issue (see docs/PIPELINE.md for the exact
comment format Workflow B's response-reading step expects), and Workflow A's
next scheduled run reads new comments to pick up your decision.
"""
import requests

from . import config

API_ROOT = f"https://api.github.com/repos/{config.GITHUB_REPOSITORY}"


def _headers():
    return {
        "Authorization": f"Bearer {config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }


def create_deck_issue(title: str, body: str, labels: list[str]) -> dict:
    resp = requests.post(
        f"{API_ROOT}/issues",
        headers=_headers(),
        json={"title": title, "body": body, "labels": labels},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return {"number": data["number"], "url": data["html_url"]}


def comment_on_issue(issue_number: int, body: str) -> None:
    resp = requests.post(
        f"{API_ROOT}/issues/{issue_number}/comments",
        headers=_headers(),
        json={"body": body},
        timeout=30,
    )
    resp.raise_for_status()


def close_issue(issue_number: int) -> None:
    resp = requests.patch(
        f"{API_ROOT}/issues/{issue_number}",
        headers=_headers(),
        json={"state": "closed"},
        timeout=30,
    )
    resp.raise_for_status()


def get_new_comments(issue_number: int, since_iso: str | None = None) -> list[dict]:
    params = {"since": since_iso} if since_iso else {}
    resp = requests.get(
        f"{API_ROOT}/issues/{issue_number}/comments",
        headers=_headers(),
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    return [{"body": c["body"], "created_at": c["created_at"], "user": c["user"]["login"]}
            for c in resp.json()]


def list_open_deck_issues(label: str) -> list[dict]:
    resp = requests.get(
        f"{API_ROOT}/issues",
        headers=_headers(),
        params={"state": "open", "labels": label},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
