import os

import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
API = "https://api.github.com"


def list_open_issues(repo):
    response = requests.get(
        f"{API}/repos/{repo}/issues",
        headers={"Authorization": f"token {GITHUB_TOKEN}"},
        params={"state": "open"},
        timeout=10,
    )
    response.raise_for_status()
    return [issue["title"] for issue in response.json()]
