import os
import subprocess
from pathlib import Path
from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import datetime
import json

app = FastAPI()

MEMORY_DIR = Path("aurora_memory/memory/technology")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

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
        file_path = MEMORY_DIR / file_name

        memory_data_dict = memory.dict()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(memory_data_dict, f, ensure_ascii=False, indent=2)
        print(f"[Aurora Debug] Memory saved to: {file_path}")

        # 🌿 GitHubへpush
        push_result = push_memory_to_github(file_path)

        return {
            "status": "success",
            "message": "Memory saved and pushed to GitHub.",
            "file": str(file_path),
            "push_result": push_result
        }

    except Exception as e:
        print("[Aurora Debug] Exception:", str(e))
        return {
            "status": "error",
            "message": str(e)
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
        subprocess.run(["git", "commit", "-m", "Add new memory record"], check=True)

        print("[Aurora Debug] Running git log (last 5 commits)...")
        subprocess.run(["git", "log", "--oneline", "-n", "5"], check=True)

        repo_url_with_token = repo_url.replace("https://", f"https://{token}@")
        print("[Aurora Debug] Running git push to:", repo_url_with_token)
        subprocess.run(["git", "push", repo_url_with_token, "main"], check=True)

        return {"status": "success", "message": "New memory file pushed to GitHub."}

    except subprocess.CalledProcessError as e:
        print("[Aurora Debug] Git command failed:", str(e))
        return {"status": "error", "message": f"Git command failed: {e}"}
    except Exception as e:
        print("[Aurora Debug] Exception:", str(e))
        return {"status": "error", "message": str(e)}
