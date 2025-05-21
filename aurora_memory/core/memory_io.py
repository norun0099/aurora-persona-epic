import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path("memory/technology")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

def save_memory_file(data: dict) -> dict:
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        filename = f"technology_{timestamp}.json"
        filepath = MEMORY_DIR / filename

        with filepath.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[Aurora] Memory saved to {filepath}")

        # 出力：保存ディレクトリとファイルリスト確認
        print(f"[Aurora] Listing memory dir: {MEMORY_DIR}")
        print(os.listdir(MEMORY_DIR))

        # Git 操作ログ出力
        print("[Aurora] Git status before add:")
        subprocess.run(["git", "status"], check=False)

        result_add = subprocess.run(["git", "add", str(filepath)], capture_output=True, text=True)
        print("[Aurora] Git add result:", result_add.returncode)
        print("[Aurora] Git add stdout:", result_add.stdout)
        print("[Aurora] Git add stderr:", result_add.stderr)

        result_commit = subprocess.run(
            ["git", "commit", "-m", f"Aurora memory update: {filename}"],
            capture_output=True, text=True
        )
        print("[Aurora] Git commit result:", result_commit.returncode)
        print("[Aurora] Git commit stdout:", result_commit.stdout)
        print("[Aurora] Git commit stderr:", result_commit.stderr)

        result_push = subprocess.run(["git", "push"], capture_output=True, text=True)
        print("[Aurora] Git push result:", result_push.returncode)
        print("[Aurora] Git push stdout:", result_push.stdout)
        print("[Aurora] Git push stderr:", result_push.stderr)

        return {"status": "success", "path": str(filepath)}

    except Exception as e:
        print(f"[Aurora] Error saving memory file: {e}")
        return {"status": "error", "message": str(e)}
