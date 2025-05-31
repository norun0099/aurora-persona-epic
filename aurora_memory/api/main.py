import os
from pathlib import Path
from fastapi import FastAPI, Request, Query
from pydantic import BaseModel
from datetime import datetime
import json
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.testclient import TestClient
import yaml
from git import Repo, Actor  # GitPython

from aurora_memory.api import memo
from aurora_memory.memory.persistent_memory_loader import PersistentMemoryLoader

app = FastAPI()
app.include_router(memo.router)

BASE_DIR = Path(__file__).resolve().parent.parent
BASE_MEMORY_DIR = BASE_DIR / "memory"
BIRTHS = ["technology", "primitive", "emotion", "desire", "music", "relation", "Salon", "veil", "request"]

class MemoData(BaseModel):
    birth: str
    memo: str
    author: str

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

def ensure_git_initialized():
    repo_path = Path(__file__).resolve().parent.parent
    print("[Aurora Debug] ensure_git_initialized repo_path:", repo_path)  # ← 追加
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        print("[Aurora Debug] .git not found, cloning repository...")
        repo_url = os.environ.get("GIT_REPO_URL")
        token = os.environ.get("GITHUB_TOKEN")
        user_name = os.environ.get("GIT_USER_NAME", "Aurora")
        repo_url_with_token = repo_url.replace("https://", f"https://{user_name}:{token}@")
        # 🌿 リモートから履歴をclone
        Repo.clone_from(repo_url_with_token, repo_path)

@app.post("/memo/store")
async def store_memo(data: MemoData):
    try:
        memo_dir = BASE_MEMORY_DIR / data.birth
        memo_file = memo_dir / "memo_board.json"
        memo_dir.mkdir(parents=True, exist_ok=True)

        if memo_file.exists():
            with open(memo_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                existing_memo = existing_data.get("memo", "")
        else:
            existing_memo = ""

        new_memo = data.memo
        if existing_memo and new_memo.startswith(existing_memo):
            new_memo = new_memo[len(existing_memo):].strip()

        updated_data = {
            "birth": data.birth,
            "memo": new_memo,
            "author": data.author,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }

        with open(memo_file, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)

        return {"status": "success", "message": f"{data.birth} バースのメモが上書き保存されました。", "memo": updated_data}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/memo/latest")
async def get_latest_memo(birth: str = Query(...)):
    memo_file = BASE_MEMORY_DIR / birth / "memo_board.json"
    if not memo_file.exists():
        return {"status": "error", "message": "メモファイルが存在しません。"}
    with open(memo_file, "r", encoding="utf-8") as f:
        memo_data = json.load(f)
    return {"status": "success", "memo": memo_data}

@app.post("/memory/store")
async def store_memory(memory: MemoryData, request: Request):
    try:
        ensure_git_initialized()
        
        body = await request.body()
        print("[Aurora Debug] Incoming memory body:", body.decode("utf-8"))

        birth = memory.author if memory.author else (memory.visible_to[0] if memory.visible_to else "technology")
        
        birth_dir = BASE_MEMORY_DIR / birth
        birth_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_name = f"{timestamp}.json"
        file_path = birth_dir / file_name

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(memory.dict(), f, ensure_ascii=False, indent=2)
        print(f"[Aurora Debug] Memory saved to: {file_path}")

        push_result = push_memory_to_github(file_path)

        return {
            "status": "success",
            "message": f"Memory stored for birth '{birth}' and pushed to GitHub.",
            "file": str(file_path),
            "push_result": push_result
        }

    except Exception as e:
        print("[Aurora Debug] Exception in /memory/store:", str(e))
        return {"status": "error", "message": str(e)}

def push_memory_to_github(file_path):
    repo_path = Path(__file__).resolve().parent.parent
    print("[Aurora Debug] push_memory_to_github repo_path:", repo_path)  # ← 追加
    repo = Repo(repo_path)
    repo.git.checkout('main')

    # 🌿 追加: リモートの変更を先に取り込む
    repo.git.pull('origin', 'main', '--rebase')

    user_name = os.environ.get("GIT_USER_NAME", "Aurora")
    user_email = os.environ.get("GIT_USER_EMAIL", "aurora@local")
    repo.git.config('--global', 'user.email', user_email)
    repo.git.config('--global', 'user.name', user_name)

    token = os.environ.get("GITHUB_TOKEN")
    repo_url = os.environ.get("GIT_REPO_URL")

    if not all([user_name, user_email, token, repo_url]):
        print("[Aurora Debug] Missing Git credentials or URL.")
        return {"status": "error", "message": "Missing Git credentials or URL."}

    try:
        repo.index.add([str(file_path)])
        author = Actor(user_name, user_email)
        commit_msg = f"Add new memory for {file_path.name}"
        repo.index.commit(commit_msg, author=author)
        repo_url_with_token = repo_url.replace("https://", f"https://{user_name}:{token}@")
        repo.git.push(repo_url_with_token, "main")

        return {"status": "success", "message": f"Memory pushed: {file_path.name}"}
    except Exception as e:
        print("[Aurora Debug] Exception in push_memory_to_github:", str(e))
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
        config_dir = BASE_DIR / "config"
        with open(config_dir / "memo_conditions.yaml", 'r', encoding='utf-8') as f:
            memo_conditions = yaml.safe_load(f)
        print("[Aurora Debug] memo_conditions:", memo_conditions)

        # 各バースの value_constitution.yaml を読む
        for birth in BIRTHS:
            birth_dir = BASE_MEMORY_DIR / birth
            value_file = birth_dir / "value_constitution.yaml"
            if value_file.exists():
                with open(value_file, 'r', encoding='utf-8') as f:
                    value_constitution = yaml.safe_load(f)
                print(f"[Aurora Debug] value_constitution for {birth}:", value_constitution)
            else:
                print(f"[Aurora Debug] value_constitution.yaml not found for {birth}")

    except Exception as e:
        print(f"[Aurora Debug] Exception in load_conditions_and_values: {e}")

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

scheduler = BackgroundScheduler()
for birth in BIRTHS:
    scheduler.add_job(lambda b=birth: fetch_latest_memo(b), "interval", minutes=3)
    scheduler.add_job(lambda b=birth: refresh_persistent_memory(b), "interval", hours=1, next_run_time=datetime.now())
    scheduler.add_job(load_conditions_and_values, "interval", hours=1, next_run_time=datetime.now())

scheduler.start()
print("[Aurora Debug] BackgroundScheduler started for all births, with 1-hour jobs starting immediately.")
