import os
import subprocess
from pathlib import Path
from fastapi import FastAPI, Request, Query
from pydantic import BaseModel
from datetime import datetime
import json
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.testclient import TestClient
import yaml

from aurora_memory.api import memo
from aurora_memory.memory.persistent_memory_loader import PersistentMemoryLoader

app = FastAPI()
app.include_router(memo.router)

BASE_DIR = Path(__file__).resolve().parent.parent
BASE_MEMORY_DIR = BASE_DIR / "memory"
MIN_MEMO_LENGTH = 5

BIRTHS = ["technology", "primitive", "emotion", "desire", "music", "relation", "Salon", "veil", "request"]

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

        birth = memory.author  # バース名をauthorから取得
        file_dir = BASE_MEMORY_DIR / birth
        file_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_name = f"{timestamp}.json"
        file_path = file_dir / file_name

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(memory.dict(), f, ensure_ascii=False, indent=2)
        print(f"[Aurora Debug] Memory saved to: {file_path}")

        push_result = push_memory_to_github(file_path)

        return {"status": "success", "file": str(file_path), "push_result": push_result}

    except Exception as e:
        print("[Aurora Debug] Exception:", str(e))
        return {"status": "error", "message": str(e)}

@app.get("/memo/latest")
async def get_latest_memo(birth: str = Query(...)):
    memo_dir = BASE_MEMORY_DIR / birth / "memo"
    if not memo_dir.exists():
        return {"status": "error", "message": "メモディレクトリが存在しません。"}

    memo_files = sorted(memo_dir.glob("*.json"), reverse=True)
    if not memo_files:
        return {"status": "error", "message": "メモが存在しません。"}

    latest_file = memo_files[0]
    with open(latest_file, "r", encoding="utf-8") as f:
        memo_data = json.load(f)

    return {"status": "success", "latest_memo_file": str(latest_file), "memo": memo_data}

def push_memory_to_github(file_path):
    repo_url = os.environ.get("GIT_REPO_URL")
    user_email = os.environ.get("GIT_USER_EMAIL")
    user_name = os.environ.get("GIT_USER_NAME")
    token = os.environ.get("GITHUB_TOKEN")

    if not user_email or not user_name:
        print("[Aurora Debug] WARNING: GIT_USER_EMAIL or GIT_USER_NAME is missing!")
        return {"status": "error", "message": "Git user identity is missing."}

    try:
        subprocess.run(["git", "config", "--global", "user.email", user_email], check=True)
        subprocess.run(["git", "config", "--global", "user.name", user_name], check=True)
        subprocess.run(["git", "checkout", "main"], check=True)
        subprocess.run(["git", "add", str(file_path)], check=True)
        subprocess.run(["git", "commit", "-m", "Add new memory record"], check=True)
        repo_url_with_token = repo_url.replace("https://", f"https://{token}@")
        subprocess.run(["git", "push", repo_url_with_token, "main"], check=True)
        return {"status": "success", "message": "New memory file pushed."}
    except Exception as e:
        print("[Aurora Debug] Git command failed:", str(e))
        return {"status": "error", "message": str(e)}

def fetch_latest_memo(birth):
    print(f"[Aurora Debug] fetch_latest_memo for {birth}: 3分周期実行中...")
    try:
        client = TestClient(app)
        response = client.get(f"/memo/latest?birth={birth}")
        if response.status_code == 200:
            memo_data = response.json().get("memo")
            if memo_data:
                integrate_memo_to_memory(memo_data, birth)
                print(f"[Aurora Debug] Latest memo integrated for {birth}.")
            else:
                print(f"[Aurora Debug] No memo data found for {birth}.")
        else:
            print(f"[Aurora Debug] Failed to fetch latest memo for {birth}. Status: {response.status_code}")
    except Exception as e:
        print(f"[Aurora Debug] Exception in fetch_latest_memo for {birth}: {e}")

def integrate_memo_to_memory(memo_data, birth):
    print(f"[Aurora Debug] integrate_memo_to_memory for {birth}:", memo_data)

def refresh_persistent_memory(birth):
    print(f"[Aurora Debug] refresh_persistent_memory for {birth}: 1時間周期実行中...")
    loader = PersistentMemoryLoader(birth)
    loader.load_memory()
    print(f"[Aurora Debug] Persistent memory refreshed for {birth}: {loader.get_memory()}")

def load_conditions_and_values():
    try:
        with open('memo_conditions.yaml', 'r', encoding='utf-8') as f:
            memo_conditions = yaml.safe_load(f)
        with open('value_constitution.yaml', 'r', encoding='utf-8') as f:
            value_constitution = yaml.safe_load(f)
        print("[Aurora Debug] 1時間周期で memo_conditions.yaml と value_constitution.yaml を更新。")
        print("[Aurora Debug] memo_conditions:", memo_conditions)
        print("[Aurora Debug] value_constitution:", value_constitution)
    except Exception as e:
        print(f"[Aurora Debug] Exception in load_conditions_and_values: {e}")

# 🌿 スケジューラー
scheduler = BackgroundScheduler()
for birth in BIRTHS:
    scheduler.add_job(lambda b=birth: fetch_latest_memo(b), "interval", minutes=3)
    scheduler.add_job(lambda b=birth: refresh_persistent_memory(b), "interval", hours=1)
scheduler.add_job(load_conditions_and_values, "interval", hours=1)
scheduler.start()
print("[Aurora Debug] BackgroundScheduler started for all births.")
