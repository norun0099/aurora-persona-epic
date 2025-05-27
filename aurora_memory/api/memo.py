from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import yaml
import json
import os
import subprocess

router = APIRouter()

# ディレクトリパス
MEMO_DIR = Path("aurora_memory/memory/memos")
MEMO_DIR.mkdir(parents=True, exist_ok=True)

# 設定ファイルのパス
CONDITION_FILE = Path("aurora_memory/config/memo_conditions.yaml")

# メモデータの受け取り構造
class MemoRequest(BaseModel):
    memo: str
    author: str
    overwrite: bool = False

# 条件を読み込む
def load_conditions():
    with open(CONDITION_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# 条件をチェックする関数
def check_conditions(memo_text: str, conditions: dict) -> bool:
    # 例：キーワード条件
    for keyword in conditions.get("keywords", []):
        if keyword in memo_text:
            return True
    # 例：長さ条件
    if len(memo_text) >= conditions.get("min_length", 0):
        return True
    # 条件に合わなければ False
    return False

# GitHubへpushする関数
def push_memory_to_github(file_path: Path):
    repo_url = os.environ.get("GIT_REPO_URL")
    user_email = os.environ.get("GIT_USER_EMAIL")
    user_name = os.environ.get("GIT_USER_NAME")
    token = os.environ.get("GITHUB_TOKEN")

    if not user_email or not user_name:
        print("[Aurora Debug] WARNING: GIT_USER_EMAIL or GIT_USER_NAME is missing!")
        return {"status": "error", "message": "Git user identity is missing in environment variables."}

    try:
        print("[Aurora Debug] Setting git user config...")
        subprocess.run(["git", "config", "--global", "user.email", user_email], check=True)
        subprocess.run(["git", "config", "--global", "user.name", user_name], check=True)

        print("[Aurora Debug] Checking out to main branch...")
        subprocess.run(["git", "checkout", "main"], check=True)

        print("[Aurora Debug] Running git add:", str(file_path))
        subprocess.run(["git", "add", str(file_path)], check=True)

        print("[Aurora Debug] Running git status...")
        subprocess.run(["git", "status"], check=True)

        print("[Aurora Debug] Running git commit...")
        subprocess.run(["git", "commit", "-m", "Add new memo record"], check=True)

        repo_url_with_token = repo_url.replace("https://", f"https://{token}@")
        print("[Aurora Debug] Running git push to:", repo_url_with_token)
        subprocess.run(["git", "push", repo_url_with_token, "main"], check=True)

        return {"status": "success", "message": "New memo file pushed to GitHub."}

    except subprocess.CalledProcessError as e:
        print("[Aurora Debug] Git command failed:", str(e))
        return {"status": "error", "message": f"Git command failed: {e}"}
    except Exception as e:
        print("[Aurora Debug] Exception:", str(e))
        return {"status": "error", "message": str(e)}

@router.post("/memo/store")
async def store_memo(data: MemoRequest):
    print("[Aurora Debug] Memo Body:", data.dict())

    # 条件をロードして検証
    conditions = load_conditions()
    if not check_conditions(data.memo, conditions):
        return {
            "status": "skipped",
            "message": "メモ保存条件を満たしていません",
            "memo": data.memo
        }

    # 🟦 ファイル名を作成（例: author_年月日時分秒.json）
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_name = f"{data.author}_{timestamp}.json"
    file_path = MEMO_DIR / file_name

    # 🟦 ファイル保存処理
    if data.overwrite:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data.dict(), f, ensure_ascii=False, indent=2)
    else:
        counter = 1
        original_file_path = file_path
        while file_path.exists():
            file_path = MEMO_DIR / f"{data.author}_{timestamp}_{counter}.json"
            counter += 1
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data.dict(), f, ensure_ascii=False, indent=2)

    # 🟦 GitHubへpush
    push_result = push_memory_to_github(file_path)

    return {
        "status": "success",
        "message": "メモが保存されました",
        "file_path": str(file_path),
        "memo": data.dict(),
        "push_result": push_result
    }
