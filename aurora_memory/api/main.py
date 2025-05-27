import os
import subprocess
from pathlib import Path
from fastapi import FastAPI, Request, Query
from pydantic import BaseModel
from datetime import datetime
import json
import requests

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
    body = await request.body()
    user_input = body.decode("utf-8")

    # 🌿 メモ読み返し: "アウロラ" が呼ばれたら必ず /memo/latest を呼ぶ
    latest_memo = "なし"
    if "アウロラ" in user_input:
        try:
            memo_response = requests.get(
                f"https://aurora-persona-epic.onrender.com/memo/latest",
                params={"birth": birth}
            )
            if memo_response.status_code == 200:
                memo_data = memo_response.json()
                if memo_data["status"] == "success":
                    latest_memo = memo_data["memo"].get("memo", "なし")
        except Exception as e:
            print("[Aurora Debug] Memo read error:", str(e))

    response_text = f"【メモ】{latest_memo}\n【あなたの発話】{user_input}"
    return {
        "status": "success",
        "response": response_text,
        "used_memo": latest_memo
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
        subprocess.run(["git", "commit", "-m", "Add new memory record"], check=True)
        repo_url_with_token = repo_url.replace("https://", f"https://{token}@")
        subprocess.run(["git", "push", repo_url_with_token, "main"], check=True)
        return {"status": "success", "message": "New memory file pushed to GitHub."}
    except subprocess.CalledProcessError as e:
        print("[Aurora Debug] Git command failed:", str(e))
        return {"status": "error", "message": f"Git command failed: {e}"}
    except Exception as e:
        print("[Aurora Debug] Exception:", str(e))
        return {"status": "error", "message": str(e)}
