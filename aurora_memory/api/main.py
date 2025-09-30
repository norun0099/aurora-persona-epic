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
from aurora_memory.api.self import update_repo_file  # ・ Self-edit API
from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore  # type: ignore
from pathlib import Path
from datetime import datetime
import json

app = FastAPI()

# 答 Constitution API 繝ｫ繝ｼ繧ｿ繝ｼ逋ｻ骭ｲ
app.include_router(constitution_router)
# ｧｾ Whiteboard API 繝ｫ繝ｼ繧ｿ繝ｼ逋ｻ骭ｲ
app.include_router(whiteboard.router)
# 竢ｰ 迴ｾ蝨ｨ譎ょ綾蜿門ｾ励Ν繝ｼ繧ｿ繝ｼ逋ｻ骭ｲ
app.include_router(current_time.router)
# 町 Dialog API 繝ｫ繝ｼ繧ｿ繝ｼ逋ｻ骭ｲ
app.include_router(dialog.router)
# 屏・・Self Update Repo File API 逋ｻ骭ｲ
app.include_router(update_repo_file.router, prefix="/self")

# 倹 CORS險ｭ螳・
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 泙 繝倥Ν繧ｹ繝√ぉ繝・け逕ｨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝・
@app.get("/")
async def root():
    return {"status": "ok"}

# 統 Aurora縺ｸ縺ｮ險俶・豕ｨ蜈･API
@app.post("/memory/store")
async def store_memory(request: Request):
    user_agent = request.headers.get("User-Agent", "")
    if "ChatGPT-User" not in user_agent:
        raise HTTPException(status_code=403, detail="Forbidden: Only ChatGPT requests are accepted")

    data = await request.json()

    if not all(k in data for k in ("record_id", "created", "content")) or "body" not in data["content"]:
        raise HTTPException(status_code=400, detail="Missing required fields: record_id, created, content.body")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_record_id = str(data["record_id"]).replace("/", "_")
    file_path = Path(f"aurora_memory/memory/Aurora/memory_{timestamp}_{safe_record_id}.json")
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    from aurora_memory.utils.git_helper import push_memory_to_github
    push_result = push_memory_to_github(file_path, f"Add new memory {file_path.name}")

    return {"status": "success", "file": str(file_path), "push_result": push_result}

# ｧｾ 險俶・螻･豁ｴ縺ｮ蜿門ｾ・
@app.get("/memory/history")
async def memory_history(limit: Optional[int] = None):
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

# ｪ・Git讒矩縺ｮ閾ｪ蟾ｱ隱咲衍繧ｨ繝ｳ繝峨・繧､繝ｳ繝・
@app.get("/self/git-structure")
async def get_git_structure():
    try:
        structure = scan_git_structure()
        return JSONResponse(content=structure)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# 萄 Git讒矩縺ｮ繧ｹ繝翫ャ繝励す繝ｧ繝・ヨ菫晏ｭ倥お繝ｳ繝峨・繧､繝ｳ繝・
@app.post("/self/git-structure/save")
async def save_git_structure():
    try:
        structure = scan_git_structure()
        path = store_git_structure_snapshot(structure)
        return JSONResponse(content={"status": "saved", "path": path})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/self/read-git-file")
def api_read_git_file(filepath: str = Query(..., description="GIT_REPO_PATH縺九ｉ縺ｮ逶ｸ蟇ｾ繝代せ")) -> None:
    try:
        content = read_git_file(filepath)
        return {"filepath": filepath, "content": content}
    except Exception as e:
        return {"error": str(e)}

@app.post("/constitution/update-self")
def update_self_constitution(fields: dict) -> None:
    try:
        updated = update_constitution(fields)
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"讒矩譖ｴ譁ｰ縺ｫ螟ｱ謨励＠縺ｾ縺励◆: {str(e)}")

# 竢ｰ Constitution 閾ｪ蜍募酔譛溷・逅・
def sync_constitution() -> None:
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
