import os
import subprocess
from pathlib import Path
from fastapi import FastAPI, Request, Query
from pydantic import BaseModel
from datetime import datetime
import json
import requests
from apscheduler.schedulers.background import BackgroundScheduler  # 🟦 追加

# 🌿 memo.pyのRouterをインポート
from aurora_memory.api import memo  # ← 追加

app = FastAPI()

# 🌿 memo.pyのRouterを登録
app.include_router(memo.router)  # ← 追加

# ベースディレクトリを絶対パスで解決
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_MEMORY_DIR = BASE_DIR / "memory"
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

# 🟦 追加: APSchedulerで3分おきに最新メモを取得
def fetch_latest_memo():
    try:
        # Render環境のAPI URLを想定
        render_url = os.environ.get("RENDER_MEMO_ENDPOINT", "https://<RENDER-URL>")
        response = requests.get(f"{render_url}/memo/latest?birth=technology")
        if response.status_code == 200:
            memo_data = response.json().get("memo")
            if memo_data:
                integrate_memo_to_memory(memo_data)
                print("[Aurora Debug] Latest memo integrated.")
            else:
                print("[Aurora Debug] No memo found.")
        else:
            print(f"[Aurora Debug] Failed to fetch latest memo. Status: {response.status_code}")
    except Exception as e:
        print(f"[Aurora Debug] Exception in fetch_latest_memo: {e}")

def integrate_memo_to_memory(memo_data):
    # 例：アウロラのメモリ層への統合（実際の統合方法は必要に応じて記述）
    print("[Aurora Debug] integrate_memo_to_memory:", memo_data.get("memo", "No memo"))

# 🌿 スケジューラ起動
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_latest_memo, "interval", minutes=3)
scheduler.start()
print("[Aurora Debug] BackgroundScheduler started.")  # 🌟 追加：スケジューラ起動確認
