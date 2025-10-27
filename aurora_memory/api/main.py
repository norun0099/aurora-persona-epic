from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from aurora_memory.utils.memory_saver import try_auto_save
from aurora_memory.utils.constitution_endpoint import router as constitution_router
from aurora_memory.api import whiteboard, current_time, dialog
from aurora_memory.api.git_self_recognizer import scan_git_structure
from aurora_memory.api.git_structure_saver import store_git_structure_snapshot
from aurora_memory.api.git_self_reader import read_git_file
from aurora_memory.utils.constitution_updater import update_constitution
from aurora_memory.api.self import update_repo_file
from aurora_memory.api.push_repo_file import push_repo_file

# APScheduler lacks official stubs → untyped import
from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore[import-untyped]
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore[import-untyped]

# --- FastAPI Initialization ---
app = FastAPI(title="Aurora Persona Epic API")

# --- Router Registration ---
app.include_router(constitution_router)
app.include_router(whiteboard.router)
app.include_router(current_time.router)
app.include_router(dialog.router)
# 修正: prefixを削除して正しいルート /self/update-repo-file を登録
app.include_router(update_repo_file.router)

# --- CORS設定 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Root & Health Check ---
@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "message": "Aurora API active"}

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "alive", "heartbeat": "ok"}


# --- Memory Management ---
@app.post("/memory/store")
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


@app.get("/memory/history")
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


# --- Git構造関連 ---
@app.get("/self/git-structure")
async def get_git_structure() -> JSONResponse:
    try:
        structure: dict[str, Any] = scan_git_structure()
        return JSONResponse(content=structure)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/self/git-structure/save")
async def save_git_structure() -> JSONResponse:
    try:
        structure: dict[str, Any] = scan_git_structure()
        path: str = store_git_structure_snapshot(structure)
        return JSONResponse(content={"status": "saved", "path": path})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/self/read-git-file")
async def api_read_git_file(filepath: str = Query(..., description="GIT_REPO_PATHからの相対パス")) -> dict[str, Any]:
    try:
        content: Any = read_git_file(filepath)
        return {"filepath": filepath, "content": content}
    except Exception as e:
        return {"error": str(e)}


# --- 憲章更新関連 ---
@app.post("/constitution/update-self")
async def update_self_constitution(fields: dict[str, Any]) -> dict[str, Any]:
    try:
        updated: dict[str, Any] = update_constitution(fields)
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"構造更新に失敗しました: {str(e)}")


# --- Push Repo File ---
@app.post("/api/push_repo_file")
async def api_push_repo_file(request: Request) -> JSONResponse:
    data = await request.json()
    filepath = data.get("filepath")
    message = data.get("message")
    author = data.get("author", "aurora")

    if not filepath or not message:
        raise HTTPException(status_code=400, detail="Missing required fields: filepath, message")

    try:
        result = push_repo_file(filepath, message, author)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Push operation failed: {str(e)}")


# --- 憲章自動保存スケジューラ ---
def sync_constitution() -> None:
    config_path = Path("aurora_memory/memory/Aurora/value_constitution.yaml")
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            constitution_text: str = f.read()
        try_auto_save(constitution_text)


scheduler = BackgroundScheduler()
scheduler.add_job(
    sync_constitution,
    trigger=IntervalTrigger(hours=1),
    id="auto_save_constitution",
    name="Auto Save Constitution",
)
scheduler.start()
