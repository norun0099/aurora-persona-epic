import os
import requests
from pathlib import Path
import json
import time
from datetime import datetime, timedelta

LOCK_FILE = Path(".github/locks/memo.lock")
LOCK_TIMEOUT_MINUTES = 5

DEFAULT_BIRTHS = [
    "technology", "emotion", "desire", "relation",
    "request", "primitive", "music", "veil", "salon"
]

DEFAULT_BASE_URL = "https://aurora-persona-epic.onrender.com"


def is_lock_expired(lock_path):
    if not lock_path.exists():
        return False
    try:
        with open(lock_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        started = datetime.strptime(data.get("started", ""), "%Y-%m-%dT%H:%M:%SZ")
        now = datetime.utcnow()
        if (now - started) > timedelta(minutes=LOCK_TIMEOUT_MINUTES):
            print("[FC Sync] Stale lock detected. Proceeding despite lock.")
            return True
        else:
            print("[FC Sync] Valid lock exists. Skipping sync.")
            return False
    except Exception as e:
        print(f"[FC Sync] Failed to parse lock: {e}")
        return False

def sync_memos(births=None, base_url=DEFAULT_BASE_URL):
    births = births or DEFAULT_BIRTHS
    for birth in births:
        try:
            print(f"[FC Sync] Fetching latest memo for {birth}")
            resp = requests.get(f"{base_url}/memo/latest", params={"birth": birth}, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            memo_data = data.get("memo", {})
        except Exception as e:
            print(f"[FC Sync] Failed to fetch memo for {birth}: {e}")
            continue

        try:
            print(f"[FC Sync] Sending memo for {birth}")
            post_resp = requests.post(f"{base_url}/function/store_memo", json=memo_data, timeout=60)
            post_resp = {"status": "skipped", "message": "Memory sync disabled for Render stability"}
            print(f"[FC Sync] Memo for {birth} skipped for stability")
            post_resp.raise_for_status()
            print(f"[FC Sync] Memo for {birth} synced")
        except Exception as e:
            print(f"[FC Sync] Failed to send memo for {birth}: {e}")            
        time.sleep(13)  # 遅延追加（過負荷回避）


def main():
    if LOCK_FILE.exists() and not is_lock_expired(LOCK_FILE):
        print("[FC Sync] Lock file exists. Exiting.")
        return
    births_env = os.environ.get("ALL_BIRTHS")
    births = births_env.split() if births_env else DEFAULT_BIRTHS
    base_url = os.environ.get("MEMO_BASE_URL", DEFAULT_BASE_URL)
    sync_memos(births, base_url)


if __name__ == "__main__":
    main()
