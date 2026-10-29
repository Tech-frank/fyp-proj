import requests

GITHUB_TOKEN = "ghp_9fK2LmQx7vB1nC8dE3rT6yU0iO4pA5sD"
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
