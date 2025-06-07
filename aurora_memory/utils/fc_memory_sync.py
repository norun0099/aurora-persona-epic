import os
import requests
from pathlib import Path

DEFAULT_BIRTHS = [
    "technology", "emotion", "desire", "relation",
    "request", "primitive", "music", "veil", "salon"
]

DEFAULT_BASE_URL = "https://aurora-persona-epic.onrender.com"


def sync_memos(births=None, base_url=DEFAULT_BASE_URL):
    births = births or DEFAULT_BIRTHS
    for birth in births:
        try:
            print(f"[FC Sync] Fetching latest memo for {birth}")
            resp = requests.get(f"{base_url}/memo/latest", params={"birth": birth}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            memo_data = data.get("memo", {})
        except Exception as e:
            print(f"[FC Sync] Failed to fetch memo for {birth}: {e}")
            continue

        try:
            print(f"[FC Sync] Sending memo for {birth}")
            post_resp = requests.post(f"{base_url}/function/store_memo", json=memo_data, timeout=10)
            post_resp.raise_for_status()
            print(f"[FC Sync] Memo for {birth} synced")
        except Exception as e:
            print(f"[FC Sync] Failed to send memo for {birth}: {e}")


def main():
    births_env = os.environ.get("ALL_BIRTHS")
    births = births_env.split() if births_env else DEFAULT_BIRTHS
    base_url = os.environ.get("MEMO_BASE_URL", DEFAULT_BASE_URL)
    sync_memos(births, base_url)


if __name__ == "__main__":
    main()
