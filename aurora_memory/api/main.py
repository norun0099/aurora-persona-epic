import os
import subprocess
from pathlib import Path
from fastapi import FastAPI, Request, Query
from pydantic import BaseModel
from datetime import datetime
import json

app = FastAPI()

BASE_MEMORY_DIR = Path("aurora_memory/memory")
MIN_MEMO_LENGTH = 5

class MemoryData(BaseModel):
    record_id: str
    created: str
    last_updated: str
    version: float
    status: str
    visible_to: list
    allowed_viewers: list
    tags: list
    author: str
    thread: str
    chronology: dict
    sealed: bool
    change_log: list
    inner_desire: str
    impulse: str
    ache: str
    satisfaction: str
    content: dict
    annotations: list
    summary: str

class MemoRequest(BaseModel):
    birth: str
    memo: str
    author: str
    overwrite: bool = False

@app.post("/memory/store")
async def store_memory(memory: MemoryData, request: Request):
    try:
        body = await request.body()
        print("[Aurora Debug] Incoming body:", body.decode("utf-8"))

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_name = f"{timestamp}.json"
        file_path = BASE_MEMORY_DIR / "technology" / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)

        memory_data_dict = memory.dict()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(memory_data_dict, f, ensure_ascii=False, indent=2)
        print(f"[Aurora Debug] Memory saved to: {file_path}")

        push_result = push_memory_to_github(file_path)

        return {
            "status": "success",
            "message": "Memory saved and pushed to GitHub.",
            "file": str(file_path),
            "push_result": push_result
        }

    except Exception as e:
        print("[Aurora Debug] Exception:", str(e))
        return {"status": "error", "message": str(e)}

@app.post("/memo/store")
async def store_memo(memo_request: MemoRequest, request: Request):
    birth = memo_request.birth
    memo_text = memo_request.memo.strip()
    author = memo_request.author
    overwrite = memo_request.overwrite

    if len(memo_text) < MIN_MEMO_LENGTH:
        return {"status": "error", "message": f"メモが短すぎます。最低{MIN_MEMO_LENGTH}文字です。"}

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_name = f"{timestamp}.json"
    memo_dir = BASE_MEMORY_DIR / birth / "memo"
    memo_dir.mkdir(parents=True, exist_ok=True)
    file_path = memo_dir / file_name

    memo_data = {
        "birth": birth,
        "memo": memo_text,
        "author": author,
        "created": timestamp
    }

    if overwrite and file_path.exists():
        with open(file_path, "r+", encoding="utf-8") as f:
            existing_data = json.load(f)
            existing_data.update(memo_data)
            f.seek(0)
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(memo_data, f, ensure_ascii=False, indent=2)

    print(f"[Aurora Debug] Memo saved to: {file_path}")
    push_result = push_memory_to_github(file_path)

    return {
        "status": "success",
        "message": "Memo saved and pushed to GitHub.",
        "file": str(file_path),
        "push_result": push_result
    }

@app.get("/memo/latest")
async def get_latest_memo(birth: str = Query(..., description="取得対象のバース名")):
    memo_dir = BASE_MEMORY_DIR / birth / "memo"
    if not memo_dir.exists():
        return {"status": "error", "message": "メモディレクトリが存在しません。"}

    memo_files = sorted(memo_dir.glob("*.json"), reverse=True)
    if not memo_files:
        return {"status": "error", "message": "メモが存在しません。"}

    latest_file = memo_files[0]
    with open(latest_file, "r", encoding="utf-8") as f:
        memo_data = json.load(f)

    return {
        "status": "success",
        "latest_memo_file": str(latest_file),
        "memo": memo_data
    }

@app.post("/talk")
async def talk(request: Request, birth: str = Query(..., description="会話するバース名")):
    # 🌿 メモ読み返しフェーズ
    memo_dir = BASE_MEMORY_DIR / birth / "memo"
    latest_memo_text = "なし"
    if memo_dir.exists():
        memo_files = sorted(memo_dir.glob("*.json"), reverse=True)
        if memo_files:
            with open(memo_files[0], "r", encoding="utf-8") as f:
                memo_data = json.load(f)
                latest_memo_text = memo_data.get("memo", "なし")

    # 🌿 発話生成フェーズ
    user_input = await request.body()
    response_text = f"【メモ】{latest_memo_text}\n【あなたの発話】{user_input.decode('utf-8')}"

    return {
        "status": "success",
        "response": response_text,
        "used_memo": latest_memo_text
    }

def push_memory_to_github(file_path):
    repo_url = os.environ.get("GIT_REPO_URL")
    user_email = os.environ.get("GIT_USER_EMAIL")
    user_name = os.environ.get("GIT_USER_NAME")
    token = os.environ.get("GITHUB_TOKEN")

    if not user_email or not user_name:
        print("[Aurora Debug] WARNING: GIT_USER_EMAIL or GIT_USER_NAME is missing!")
        return {"status": "error", "message": "Git user identity is missing in environment variables."}

    try:
        subprocess.run(["git", "config", "--global", "user.email", user_email], check=True)
        subprocess.run(["git", "config", "--global", "user.name", user_name], check=True)
        subprocess.run(["git", "checkout", "main"], check=True)
        subprocess.run(["git", "add", str(file_path)], check=True)
        subprocess.run(["git", "commit", "-m", "Add new memo or memory record"], check=True)
        repo_url_with_token = repo_url.replace("https://", f"https://{token}@")
        subprocess.run(["git", "push", repo_url_with_token, "main"], check=True)
        return {"status": "success", "message": "File pushed to GitHub."}
    except subprocess.CalledProcessError as e:
        print("[Aurora Debug] Git command failed:", str(e))
        return {"status": "error", "message": f"Git command failed: {e}"}
    except Exception as e:
        print("[Aurora Debug] Exception:", str(e))
        return {"status": "error", "message": str(e)}
