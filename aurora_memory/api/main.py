from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from aurora_memory.api import memo, memory_history, git_ls
from aurora_memory.utils.git_helper import push_memory_to_github
from aurora_memory.utils.memory_saver import try_auto_save
from pathlib import Path
from datetime import datetime
from aurora_memory.utils.constitution_endpoint import router as constitution_router
import os
import json

app = FastAPI()

# 各種APIルーターを登録（必要に応じて）
app.include_router(memo.router)
app.include_router(memory_history.router)
app.include_router(git_ls.router)
app.include_router(constitution_router)

# CORS設定（必要に応じて調整）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 認証用環境変数
API_KEY = os.getenv("AURORA_API_KEY")

# 📝 Auroraへの記憶注入API（birth不要）
@app.post("/memory/store")
async def store_memory(request: Request, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.split(" ")[1]
    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid token")

    data = await request.json()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_path = Path(f"aurora_memory/memory/Aurora/memory_{timestamp}.json")
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    push_result = push_memory_to_github(file_path, f"Add new memory {file_path.name}")
    return {"status": "success", "file": str(file_path), "push_result": push_result}


# 📜 Auroraのホワイトボード注入（同様に固定構造化）
@app.post("/whiteboard/store")
async def store_whiteboard(request: Request, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.split(" ")[1]
    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid token")

    data = await request.json()
    notes = data.get("notes", "")
    wb_path = Path("aurora_memory/memory/Aurora/whiteboard.yaml")
    wb_path.parent.mkdir(parents=True, exist_ok=True)

    if wb_path.exists():
        with wb_path.open("r", encoding="utf-8") as f:
            existing = f.read()
        if existing.strip() == notes.strip():
            return {"status": "skipped", "message": "No change to whiteboard."}

    with wb_path.open("w", encoding="utf-8") as f:
        f.write(notes)

    return {"status": "success", "file": str(wb_path)}


# 🔁 Constitution 自動同期（hourly）
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

def sync_constitution():
    config_path = Path("aurora_memory/memory/Aurora/value_constitution.yaml")
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            constitution_text = f.read()
        try_auto_save(constitution_text, birth="Aurora")  # "birth" を内部的に使用している場合

scheduler = BackgroundScheduler()
scheduler.add_job(
    sync_constitution,
    trigger=IntervalTrigger(hours=1),
    id="auto_save_constitution",
    name="Auto Save Constitution"
)
scheduler.start()
