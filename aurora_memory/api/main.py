from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
import os
import subprocess
from pathlib import Path
import json
import requests

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データモデル（バリデーション用）
class MemoryData(BaseModel):
    record_id: str
    created: str
    last_updated: str
    version: float
    status: str
    visible_to: list[str]
    allowed_viewers: list[str]
    tags: list[str]
    author: str
    thread: str | None = None
    chronology: dict | None = None
    sealed: bool
    change_log: list[dict] | None = None
    inner_desire: str | None = ""
    impulse: str | None = ""
    ache: str | None = ""
    satisfaction: str | None = ""
    summary: str | None = ""          # summary フィールドを追加
    content: dict
    annotations: list[str] | None = []

BASE_DIR = Path(__file__).parent.parent
MEMORY_FILE = BASE_DIR / "memory" / "technology" / "memory.json"

@app.get("/")
async def root():
    return {"status": "ok", "message": "Aurora Memory API is running."}

@app.post("/load")
async def load_memory(request: Request):
    try:
        data = await request.json()
        result = load_memory_files()
        return JSONResponse(content={"status": "success", "data": result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/memory/store")
async def store_memory(request: Request):
    try:
        data = await request.json()

        # バリデーション
        try:
            memory_data = MemoryData(**data)
        except ValidationError as ve:
            return JSONResponse(
                status_code=422,
                content={"status": "error", "message": "Validation error", "details": ve.errors()}
            )

        # 保存
        save_memory_file(data)

        # GithubへPush
        push_result = push_memory_to_github()

        # Github Actions トリガー
        dispatch_status, dispatch_text = trigger_github_dispatch()

        return JSONResponse(
            content={
                "status": "success",
                "message": "Memory saved, pushed to GitHub, and Actions triggered.",
                "push_result": push_result,
                "actions_trigger_status": dispatch_status,
                "actions_trigger_response": dispatch_text
            }
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

def save_memory_file(data: dict) -> None:
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with MEMORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_memory_files() -> dict:
    if not MEMORY_FILE.exists():
        return {"message": "No memory file found."}
    with MEMORY_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def push_memory_to_github():
    repo_url = os.environ.get("GIT_REPO_URL")
    user_email = os.environ.get("GIT_USER_EMAIL")
    user_name = os.environ.get("GIT_USER_NAME")
    token = os.environ.get("GITHUB_TOKEN")

    if not MEMORY_FILE.exists():
        return {"status": "error", "message": "memory.json does not exist."}

    try:
        subprocess.run(["git", "config", "--global", "user.email", user_email], check=True)
        subprocess.run(["git", "config", "--global", "user.name", user_name], check=True)

        subprocess.run(["git", "add", str(MEMORY_FILE)], check=True)
        subprocess.run(["git", "commit", "-m", "Update memory.json"], check=True)
        repo_url_with_token = repo_url.replace("https://", f"https://{token}@")
        subprocess.run(["git", "push", repo_url_with_token, "main"], check=True)

        return {"status": "success", "message": "memory.json pushed to GitHub."}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Git command failed: {e}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def trigger_github_dispatch():
    github_api_url = "https://api.github.com/repos/norun0099/aurora-persona-epic/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN')}",
    }
    data = {
        "event_type": "aurora_memory_push"
    }
    response = requests.post(
        github_api_url,
        headers=headers,
        json=data
    )
    return response.status_code, response.text
