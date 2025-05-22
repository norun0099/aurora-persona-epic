import os
import json
import glob
from datetime import datetime

MEMORY_DIRECTORY = "aurora_memory/memory/technology"

def save_memory_file(data: dict) -> str:
    """記憶をJSONファイルとして保存し、GitへのPushをトリガー"""
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{MEMORY_DIRECTORY}/{timestamp}.json"
    os.makedirs(MEMORY_DIRECTORY, exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[Aurora Debug] Memory saved to {filename}")

    # Gitへの自動Push（Render内部）
    try:
        os.system(f"git add {MEMORY_DIRECTORY}/*.json")
        os.system('git config user.name "norun0099"')
        os.system('git config user.email "norun0099@example.com"')
        os.system('git commit -m "Aurora auto-push memory update"')
        github_user = "norun0099"
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            push_command = (
                f"git push https://{github_user}:{github_token}@github.com/{github_user}/aurora-persona-epic.git HEAD:main"
            )
            os.system(push_command)
        else:
            print("[Aurora Warning] GITHUB_TOKEN not found. Skipping push.")
    except Exception as e:
        print(f"[Aurora Error] Git push failed: {e}")

    return filename

def load_memory_files() -> list:
    """保存された全ての記憶ファイルを読み込む"""
    files = sorted(glob.glob(f"{MEMORY_DIRECTORY}/*.json"))
    memories = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            memories.append(json.load(f))
    return memories
