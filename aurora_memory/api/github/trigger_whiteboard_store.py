import os
import requests
from datetime import datetime
from aurora_memory.utils.whiteboard_logger import log

GITHUB_API_URL = "https://api.github.com"
REPO = "norun0099/aurora-persona-epic"
WORKFLOW_FILE = "whiteboard-store.yml"
BRANCH = "main"

def trigger_whiteboard_store():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        log("GITHUB_TOKEN not set. Cannot trigger GitHub Action.")
        return

    url = f"{GITHUB_API_URL}/repos/{REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    payload = {
        "ref": BRANCH
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 204:
            log("✅ GitHub Action 'whiteboard-store.yml' triggered successfully.")
        else:
            log(f"⚠️ Failed to trigger action: {response.status_code} - {response.text}")
    except Exception as e:
        log(f"Exception while triggering GitHub Action: {e}")
