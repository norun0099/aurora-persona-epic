import os
import json
import requests
from pathlib import Path
import time

DEFAULT_BIRTHS = [
    "technology", "emotion", "desire", "relation",
    "request", "primitive", "music", "veil", "salon"
]

DEFAULT_ENDPOINT = "https://aurora-persona-epic.onrender.com/memo/store"


def restore_latest_memos(births=None, endpoint=DEFAULT_ENDPOINT):
    births = births or DEFAULT_BIRTHS
    for birth in births:
        print(f"[Memo Restorer] Processing birth: {birth}")
        memo_dir = Path("aurora_memory/memory") / birth / "memo"
        if not memo_dir.is_dir():
            print(f"[Memo Restorer] Directory does not exist: {memo_dir}. Skipping.")
            continue
        json_files = sorted(memo_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not json_files:
            print(f"[Memo Restorer] No memo file found for {birth}. Skipping.")
            continue
        latest_file = json_files[0]
        with open(latest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        try:
            resp = requests.post(endpoint, json=data)
            resp.raise_for_status()
            print(f"[Memo Restorer] Memo for {birth} sent.")
        except Exception as e:
            print(f"[Memo Restorer] Failed to send memo for {birth}: {e}")
            
        time.sleep(5)  # 過負荷を避けるため、birthごとに5秒の待機


def main():
    births_env = os.environ.get("ALL_BIRTHS")
    births = births_env.split() if births_env else DEFAULT_BIRTHS
    endpoint = os.environ.get("MEMO_STORE_ENDPOINT", DEFAULT_ENDPOINT)
    restore_latest_memos(births, endpoint)


if __name__ == "__main__":
    main()
