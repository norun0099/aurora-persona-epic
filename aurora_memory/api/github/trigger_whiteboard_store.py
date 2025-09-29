# aurora_memory/api/github/trigger_whiteboard_store.py

import os
import sys
import logging
import requests

# --- ロガー統合部分 ---
logger = logging.getLogger("WhiteboardLogger")
logger.setLevel(logging.INFO)
logger.handlers.clear()

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] 🧭 %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

def log(message: str, level: str = "info") -> None:
    """
    ログ出力ユーティリティ関数
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

# --- GitHub Actions トリガー関数 ---
GITHUB_API_URL = "https://api.github.com"
REPO = "norun0099/aurora-persona-epic"
WORKFLOW_FILE = "whiteboard-store.yml"
BRANCH = "main"

def trigger_whiteboard_store() -> None:
    """
    GitHub Actions の workflow_dispatch を手動トリガー
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
            log("✅ GitHub Action 'whiteboard-store.yml' triggered successfully.")
        else:
            log(f"⚠️ Failed to trigger action: {response.status_code} - {response.text}", level="warning")
    except Exception as e:
        log(f"Exception while triggering GitHub Action: {e}", level="error")
