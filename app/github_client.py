# GitHub API client
# Handles all calls to the GitHub REST API

import requests

GITHUB_API = "https://api.github.com"

def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

def get_user_repos(token: str) -> list[dict]:
    """Fetch public repos for the authenticated user."""
    response = requests.get(
        f"{GITHUB_API}/user/repos",
        headers=get_headers(token),
        params={"visibility": "public", "sort": "updated", "per_page": 50}
    )
    response.raise_for_status()
    return response.json()

def get_file_content(token: str, repo_full_name: str, file_path: str) -> str | None:
    """
    Fetch the raw content of a file from a GitHub repo.
    repo_full_name format: 'owner/repo'
    """
    # Clean up path — remove leading slash if present
    file_path = file_path.lstrip("/")

    response = requests.get(
        f"{GITHUB_API}/repos/{repo_full_name}/contents/{file_path}",
        headers=get_headers(token)
    )

    if response.status_code != 200:
        return None

    data = response.json()

    # GitHub returns base64-encoded content
    if data.get("encoding") == "base64":
        import base64
        return base64.b64decode(data["content"]).decode("utf-8", errors="replace")

    return None

def get_repo_tree(token: str, repo_full_name: str) -> list[str]:
    """
    Get a flat list of all file paths in the repo (default branch).
    Useful for the agent to know what files exist.
    """
    # Get default branch first
    repo_resp = requests.get(
        f"{GITHUB_API}/repos/{repo_full_name}",
        headers=get_headers(token)
    )
    repo_resp.raise_for_status()
    default_branch = repo_resp.json().get("default_branch", "main")

    # Get full tree
    tree_resp = requests.get(
        f"{GITHUB_API}/repos/{repo_full_name}/git/trees/{default_branch}",
        headers=get_headers(token),
        params={"recursive": "1"}
    )
    tree_resp.raise_for_status()

    tree = tree_resp.json().get("tree", [])
    return [item["path"] for item in tree if item["type"] == "blob"]
