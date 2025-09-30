# aurora_memory/api/github/trigger_whiteboard_store.py

import os
import sys
import logging
import requests

# --- 繝ｭ繧ｬ繝ｼ邨ｱ蜷磯Κ蛻・---
logger = logging.getLogger("WhiteboardLogger")
logger.setLevel(logging.INFO)
logger.handlers.clear()

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] ｧｭ %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

def log(message: str, level: str = "info") -> None:
    """
    繝ｭ繧ｰ蜃ｺ蜉帙Θ繝ｼ繝・ぅ繝ｪ繝・ぅ髢｢謨ｰ
    """
    level = level.lower()
    if level == "debug":
        logger.debug(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    else:
        logger.info(message)

# --- GitHub Actions 繝医Μ繧ｬ繝ｼ髢｢謨ｰ ---
GITHUB_API_URL = "https://api.github.com"
REPO = "norun0099/aurora-persona-epic"
WORKFLOW_FILE = "whiteboard-store.yml"
BRANCH = "main"

def trigger_whiteboard_store() -> None:
    """
    GitHub Actions 縺ｮ workflow_dispatch 繧呈焔蜍輔ヨ繝ｪ繧ｬ繝ｼ
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        log("GITHUB_TOKEN not set. Cannot trigger GitHub Action.", level="error")
        return

    url = f"{GITHUB_API_URL}/repos/{REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    payload = {"ref": BRANCH}

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 204:
            log("笨・GitHub Action 'whiteboard-store.yml' triggered successfully.")
        else:
            log(f"笞・・Failed to trigger action: {response.status_code} - {response.text}", level="warning")
    except Exception as e:
        log(f"Exception while triggering GitHub Action: {e}", level="error")
