from pathlib import Path
from datetime import datetime
import requests
import json
import os
import subprocess

# 設定
RENDER_ENDPOINT = "https://aurora-persona-epic.onrender.com/whiteboard/latest"
RENDER_STORE_ENDPOINT = "https://aurora-persona-epic.onrender.com/whiteboard/store"
WHITEBOARD_PATH = Path("aurora_memory/whiteboard/whiteboard.json")

def get_render_whiteboard():
    try:
        resp = requests.get(RENDER_ENDPOINT, params={"birth": "Aurora"}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if "whiteboard" in data:
            content = json.loads(data["whiteboard"])
            return content
    except Exception as e:
        print(f"[Whiteboard Sync] Failed to load from Render: {e}")
    return None

def get_git_whiteboard():
    if WHITEBOARD_PATH.exists():
        with WHITEBOARD_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_to_git(data):
    WHITEBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    with WHITEBOARD_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    subprocess.run(["git", "add", str(WHITEBOARD_PATH)])
    subprocess.run(["git", "commit", "-m", "Sync whiteboard from Render"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("[Whiteboard Sync] Synced Render → GitHub")

def save_to_render(data):
    payload = {
        "whiteboard": json.dumps(data, ensure_ascii=False),
        "author": "aurora",
        "birth": "Aurora"
    }
    try:
        resp = requests.post(RENDER_STORE_ENDPOINT, json=payload, timeout=60)
        resp.raise_for_status()
        print("[Whiteboard Sync] Synced GitHub → Render")
    except Exception as e:
        print(f"[Whiteboard Sync] Failed to sync to Render: {e}")

def parse_timestamp(data):
    try:
        return datetime.fromisoformat(data.get("timestamp", "").replace("Z", "+00:00"))
    except Exception:
        return None

def main():
    force_push = os.environ.get("FORCE_RENDER_PUSH") == "1"
    git_data = get_git_whiteboard()
    render_data = get_render_whiteboard()

    if force_push:
        if git_data:
            save_to_render(git_data)
        else:
            print("[Whiteboard Store] Git data missing, nothing pushed to Render.")
        return

    if not git_data and not render_data:
        print("[Whiteboard Sync] No data in either source.")
        return
    elif git_data and not render_data:
        save_to_render(git_data)
    elif render_data and not git_data:
        save_to_git(render_data)
    else:
        git_time = parse_timestamp(git_data)
        render_time = parse_timestamp(render_data)
        if git_time and render_time:
            if git_time > render_time:
                save_to_render(git_data)
            elif render_time > git_time:
                save_to_git(render_data)
            else:
                print("[Whiteboard Sync] No sync needed, timestamps match.")
        else:
            print("[Whiteboard Sync] Timestamp comparison failed, fallback to Git → Render")
            save_to_render(git_data)

main()
