from pathlib import Path
from datetime import datetime
import requests
import json
import os
import subprocess

# 設定
RENDER_ENDPOINT = "https://aurora-persona-epic.onrender.com/whiteboard/latest"
RENDER_STORE_ENDPOINT = "https://aurora-persona-epic.onrender.com/whiteboard/store"
WHITEBOARD_PATH = Path("aurora_memory/memory/whiteboard/whiteboard.json")
API_KEY = os.getenv("AURORA_API_KEY")


def get_render_whiteboard() -> None:
    try:
        resp = requests.get(RENDER_ENDPOINT, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("whiteboard")
    except Exception as e:
        print(f"[Whiteboard Sync] Failed to load from Render: {e}")
    return None


def get_git_whiteboard() -> None:
    if WHITEBOARD_PATH.exists():
        try:
            with WHITEBOARD_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Whiteboard Sync] Failed to load from Git: {e}")
    return None


def save_to_git(data) -> None:
    WHITEBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    with WHITEBOARD_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Gitコミット前に差分が存在するか確認
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if result.stdout.strip():
        subprocess.run(["git", "add", str(WHITEBOARD_PATH)])
        subprocess.run(["git", "commit", "-m", "Sync whiteboard from Render"], check=False)
        subprocess.run(["git", "push"], check=False)
        print("[Whiteboard Sync] Synced Render → GitHub")
    else:
        print("[Whiteboard Sync] No changes to commit.")


def parse_timestamp(data) -> None:
    try:
        return datetime.fromisoformat(data.get("timestamp", "").replace("Z", "+00:00"))
    except Exception:
        return None


def main() -> None:
    render_data = get_render_whiteboard()
    if not render_data:
        print("[Whiteboard Sync] No data on Render. Abort Git update.")
        return

    git_data = get_git_whiteboard()
    render_time = parse_timestamp(render_data)
    git_time = parse_timestamp(git_data) if git_data else None

    if git_time and render_time:
        if render_time > git_time:
            save_to_git(render_data)
        elif git_time > render_time:
            print("[Whiteboard Sync] Render is older. No Git update performed.")
        else:
            print("[Whiteboard Sync] No sync needed, timestamps match.")
    else:
        print("[Whiteboard Sync] Timestamp comparison failed or missing. Defaulting to Render → Git.")
        save_to_git(render_data)


if __name__ == "__main__":
    main()
