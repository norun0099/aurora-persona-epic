"""
Render ↔ GitHub bridge handler.
Executes authenticated REST requests to GitHub to persist Aurora’s state.
"""

import base64
import requests
from typing import Dict, Any

# === GitHub Configuration ===
GITHUB_API = "https://api.github.com/repos/<OWNER>/<REPO>/contents/"
GITHUB_TOKEN = "<YOUR_PERSONAL_ACCESS_TOKEN>"

def push_to_repo(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sends a file update to GitHub.
    Encodes the content in base64 as required by the GitHub API.
    """
    filepath = request.get("filepath")
    content = request.get("content")
    author = request.get("author", "aurora")
    reason = request.get("reason", "automated update")

    if not filepath or not content:
        return {"status": "error", "reason": "Missing filepath or content"}

    url = f"{GITHUB_API}{filepath}"
    data = {
        "message": reason,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "committer": {"name": author, "email": "aurora@render.local"}
    }

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.put(url, json=data, headers=headers, timeout=10)
        if response.status_code in (200, 201):
            return {"status": "ok", "response": response.json()}
        else:
            return {"status": "error", "code": response.status_code, "detail": response.text}
    except Exception as e:
        return {"status": "error", "reason": str(e)}

