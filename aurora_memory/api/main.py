from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from aurora_memory.utils.memory_saver import try_auto_save, save_memory_record
from aurora_memory.utils.constitution_endpoint import router as constitution_router
from aurora_memory.api import whiteboard
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

app = FastAPI()

# 📚 Constitution API ルーター登録
app.include_router(constitution_router)
# 🧾 Whiteboard API ルーター登録
app.include_router(whiteboard.router)

# 🌐 CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🟢 ヘルスチェック用エンドポイント
@app.get("/")
async def root():
    return {"status": "ok"}

# 📝 記憶保存エンドポイント
@app.post("/memory/store")
async def store_memory(request: Request):
    user_agent = request.headers.get("User-Agent", "")
    if "ChatGPT-User" not in user_agent:
        raise HTTPException(status_code=403, detail="Forbidden: Only ChatGPT requests are accepted")

    data = await request.json()
    try:
        result = save_memory_record(data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 🧾 記憶履歴（memory/history）の取得
@app.get("/memory/history")
async def memory_history(limit: int = None):
    memory_dir = Path("aurora_memory/memory/Aurora")
    if not memory_dir.exists():
        return {"history": []}

    files = sorted(memory_dir.glob("memory_*.json"), reverse=True)
    records = []
    for fp in files:
        try:
            with fp.open("r", encoding="utf-8") as f:
                record = json.load(f)
            records.append(record)
        except Exception:
            continue
        if limit and len(records) >= limit:
            break

    return {"history": records}

# ⏰ Constitution 自動同期処理
def sync_constitution():
    config_path = Path("aurora_memory/memory/Aurora/value_constitution.yaml")
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            constitution_text = f.read()
        try_auto_save(constitution_text)

scheduler = BackgroundScheduler()
scheduler.add_job(
    sync_constitution,
    trigger=IntervalTrigger(hours=1),
    id="auto_save_constitution",
    name="Auto Save Constitution"
)
scheduler.start()
