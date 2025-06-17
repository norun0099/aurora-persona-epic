import os
import requests
import json
from datetime import datetime
from pathlib import Path

RENDER_ENDPOINT = "https://aurora-persona-epic.onrender.com/function/store_whiteboard"
WHITEBOARD_PATH = Path("aurora_memory/whiteboard/whiteboard.json")


def load_whiteboard():
    if not WHITEBOARD_PATH.exists():
        return []
    with WHITEBOARD_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("entries", [])


def store_whiteboard(entries):
    payload = {
        "whiteboard": json.dumps({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "entries": entries
        }, ensure_ascii=False),
        "author": "aurora",
        "birth": "Aurora"
    }
    try:
        resp = requests.post(RENDER_ENDPOINT, json=payload, timeout=60)
        resp.raise_for_status()
        print("[Whiteboard Sync] Successfully synced to Render.")
    except Exception as e:
        print(f"[Whiteboard Sync] Failed to sync: {e}")


def main():
    entries = load_whiteboard()
    if not entries:
        print("[Whiteboard Sync] No entries to sync.")
        return
    store_whiteboard(entries)


if __name__ == "__main__":
    main()
