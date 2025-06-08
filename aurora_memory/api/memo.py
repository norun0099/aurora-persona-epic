from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import yaml
import json
import os
import subprocess
from aurora_memory.utils.gpt_sender import send_memo_to_gpt

router = APIRouter()

# 設定ファイルのパス
CONDITION_FILE = Path("aurora_memory/config/memo_conditions.yaml")

# メモデータの受け取り構造
class MemoRequest(BaseModel):
    birth: str
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

    # 保存先ディレクトリを birth に基づいて決定
    memo_dir = Path("aurora_memory/memory") / data.birth / "memo"
    memo_dir.mkdir(parents=True, exist_ok=True)

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
    file_path = memo_dir / file_name

    # 🟦 ファイル保存処理
    if data.overwrite:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data.dict(), f, ensure_ascii=False, indent=2)
    else:
        counter = 1
        while file_path.exists():
            file_path = memo_dir / f"{data.author}_{timestamp}_{counter}.json"
            counter += 1
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data.dict(), f, ensure_ascii=False, indent=2)

    # 🟦 GitHubへpush
    # push_result = push_memory_to_github(file_path)
    push_result = {"status": "skipped", "message": "Push disabled for stability"}
    
    gpt_result = send_memo_to_gpt(data.birth, data.memo)

    return {
        "status": "success",
        "message": "メモが保存されました",
        "file_path": str(file_path),
        "memo": data.dict(),
        "push_result": push_result,
        "gpt_result": gpt_result,
    }
from typing import Optional
import shutil

@router.get("/memo/latest")
async def get_latest_memo(birth: str):
    """
    Gitに保存された birth ごとの最新メモを Render 上の一時メモディレクトリへコピーし、内容を返す。
    """
    source_dir = Path("aurora_memory/memory") / birth / "memo"
    temp_dir = Path("aurora_memory/memory/memos")
    temp_dir.mkdir(parents=True, exist_ok=True)

    if not source_dir.exists():
        raise HTTPException(status_code=404, detail=f"birth '{birth}' のメモディレクトリが存在しません")

    json_files = list(source_dir.glob("*.json"))
    if not json_files:
        raise HTTPException(status_code=404, detail=f"birth '{birth}' にメモファイルが存在しません")

    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
    temp_path = temp_dir / latest_file.name

    shutil.copy(latest_file, temp_path)

    with open(temp_path, "r", encoding="utf-8") as f:
        memo_data = json.load(f)

    return {
        "status": "success",
        "birth": birth,
        "copied_to": str(temp_path),
        "memo": memo_data
    }

@router.post("/function/store_memo")
async def store_memo_via_function(data: MemoRequest):
    """
    FunctionCalling 経由でメモをRAMに保存するための簡易API。
    """
    return await store_memo(data)
