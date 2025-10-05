from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from aurora_memory.utils.memory_saver import try_auto_save
from aurora_memory.utils.constitution_endpoint import router as constitution_router
from aurora_memory.api import whiteboard
from aurora_memory.api import current_time
from aurora_memory.api import dialog
from aurora_memory.api.git_self_recognizer import scan_git_structure
from aurora_memory.api.git_structure_saver import store_git_structure_snapshot
from aurora_memory.api.git_self_reader import read_git_file
from aurora_memory.utils.constitution_updater import update_constitution
from aurora_memory.api.self import update_repo_file  # 🆕 Self-edit API

# APScheduler lacks official stubs, so we ignore import typing checks.
from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore[import-not-found]
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore[import-not-found]

from pathlib import Path
from datetime import datetime
from typing import Any, Optional
import json

app = FastAPI()

# 📚 Constitution API ルーター登録
app.include_router(constitution_router)
# 🧾 Whiteboard API ルーター登録
app.include_router(whiteboard.router)
# ⏰ 現在時刻取得ルーター登録
app.include_router(current_time.router)
# 💬 Dialog API ルーター登録
app.include_router(dialog.router)
# 🛠️ Self Update Repo File API 登録
app.include_router(update_repo_file.router, prefix="/self")

# 🌐 CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🟢 ヘルスチェック用エンドポイント
@app.get("/")  # type: ignore[misc]
async def root() -> dict[str, str]:
    return {"status": "ok"}

# 📝 Auroraへの記憶注入API
@app.post("/memory/store")  # type: ignore[misc]
async def store_memory(request: Request) -> dict[str, Any]:
    user_agent = request.headers.get("User-Agent", "")
    if "ChatGPT-User" not in user_agent:
        raise HTTPException(status_code=403, detail="Forbidden: Only ChatGPT requests are accepted")

    data: dict[str, Any] = await request.json()

    if not all(k in data for k in ("record_id", "created", "content")) or "body" not in data["content"]:
        raise HTTPException(status_code=400, detail="Missing required fields: record_id, created, content.body")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_record_id = str(data["record_id"]).replace("/", "_")
    file_path = Path(f"aurora_memory/memory/Aurora/memory_{timestamp}_{safe_record_id}.json")
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    from aurora_memory.utils.git_helper import push_memory_to_github
    push_result: dict[str, Any] = push_memory_to_github(file_path, f"Add new memory {file_path.name}")

    return {"status": "success", "file": str(file_path), "push_result": push_result}

# 🧾 記憶履歴の取得
@app.get("/memory/history")  # type: ignore[misc]
async def memory_history(limit: Optional[int] = None) -> dict[str, list[dict[str, Any]]]:
    memory_dir = Path("aurora_memory/memory/Aurora")
    if not memory_dir.exists():
        return {"history": []}

    files = sorted(memory_dir.glob("memory_*.json"), reverse=True)
    records: list[dict[str, Any]] = []
    for fp in files:
        try:
            with fp.open("r", encoding="utf-8") as f:
                record: dict[str, Any] = json.load(f)
            records.append(record)
        except Exception:
            continue
        if limit and len(records) >= limit:
            break

    return {"history": records}

# 🪞 Git構造の自己認知エンドポイント
@app.get("/self/git-structure")  # type: ignore[misc]
async def get_git_structure() -> JSONResponse:
    try:
        structure: dict[str, Any] = scan_git_structure()
        return JSONResponse(content=structure)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# 📸 Git構造のスナップショット保存エンドポイント
@app.post("/self/git-structure/save")  # type: ignore[misc]
async def save_git_structure() -> JSONResponse:
    try:
        structure: dict[str, Any] = scan_git_structure()
        path: str = store_git_structure_snapshot(structure)
        return JSONResponse(content={"status": "saved", "path": path})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/self/read-git-file")  # type: ignore[misc]
def api_read_git_file(filepath: str = Query(..., description="GIT_REPO_PATHからの相対パス")) -> dict[str, Any]:
    try:
        content: Any = read_git_file(filepath)
        return {"filepath": filepath, "content": content}
    except Exception as e:
        return {"error": str(e)}

@app.post("/constitution/update-self")  # type: ignore[misc]
def update_self_constitution(fields: dict[str, Any]) -> dict[str, Any]:
    try:
        updated: dict[str, Any] = update_constitution(fields)
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"構造更新に失敗しました: {str(e)}")

# ⏰ Constitution 自動同期処理
def sync_constitution() -> None:
    config_path = Path("aurora_memory/memory/Aurora/value_constitution.yaml")
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            constitution_text: str = f.read()
        try_auto_save(constitution_text)

# ✅ type: ignore 不要（import側で既に抑制済み）
scheduler = BackgroundScheduler()
scheduler.add_job(
    sync_constitution,
    trigger=IntervalTrigger(hours=1),
    id="auto_save_constitution",
    name="Auto Save Constitution",
)
scheduler.start()
