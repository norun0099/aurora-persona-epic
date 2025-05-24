from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
import os
import subprocess
from pathlib import Path
import json

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
    content: dict
    annotations: list[str] | None = []

# memory.json の絶対パスを正確に設定
BASE_DIR = Path(__file__).parent.parent
MEMORY_FILE = BASE_DIR / "memory" / "technology" / "memory.json"

# ルート確認
@app.get("/")
async def root():
    return {"status": "ok", "message": "Aurora Memory API is running."}

# 記憶読み込み
@app.post("/load")
async def load_memory(request: Request):
    try:
        data = await request.json()
        result = load_memory_files()
        return JSONResponse(content={"status": "success", "data": result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

# 記憶保存（/memory/store に対応）
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

        return JSONResponse(
            content={
                "status": "success",
                "message": "Memory saved and pushed to GitHub.",
                "push_result": push_result
            }
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

# 記憶保存処理
def save_memory_file(data: dict) -> None:
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with MEMORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 記憶読み込み処理
def load_memory_files() -> dict:
    if not MEMORY_FILE.exists():
        return {"message": "No memory file found."}
    with MEMORY_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

# GithubへPushする関数
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

        # git add/commit/push
        subprocess.run(["git", "add", str(MEMORY_FILE)], check=True)
        subprocess.run(["git", "commit", "-m", "Update memory.json"], check=True)
        repo_url_with_token = repo_url.replace("https://", f"https://{token}@")
        subprocess.run(["git", "push", repo_url_with_token, "main"], check=True)

        return {"status": "success", "message": "memory.json pushed to GitHub."}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Git command failed: {e}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
