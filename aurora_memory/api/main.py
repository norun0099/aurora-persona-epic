from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from aurora_memory.api import memo, memory_history, git_ls
from aurora_memory.utils.git_helper import ensure_git_initialized, push_memory_to_github
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from aurora_memory.config.memo_conditions import load_conditions
from aurora_memory.utils.memo_trigger import trigger_auto_memo
from aurora_memory.utils.memory_saver import try_auto_save
from aurora_memory.utils.memory_quality import evaluate_quality
from aurora_memory.core.memory_io import save_memory_file
import uvicorn
import os
import json
from pathlib import Path
from datetime import datetime

app = FastAPI()
app.include_router(memo.router)
app.include_router(memory_history.router)
app.include_router(git_ls.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BIRTHS = [
    "technology", "emotion", "desire", "relation", "request", "primitive", "music", "veil", "salon"
]

@app.post("/memory/store")
async def store_memory(request: Request):
    data = await request.json()
    birth = data.get("birth")
    if birth not in BIRTHS:
        return JSONResponse(status_code=400, content={"message": "Invalid birth type."})

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_path = Path(f"aurora_memory/memory/{birth}/memory_{timestamp}.json")
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    push_result = push_memory_to_github(file_path, f"Add new memory for {file_path.name}")

    return {"status": "success", "file": str(file_path), "push_result": push_result}

scheduler = BackgroundScheduler()

for birth in BIRTHS:
    scheduler.add_job(
        lambda b=birth: try_auto_save("", birth=b),
        trigger=IntervalTrigger(hours=1),
        id=f"auto_save_{birth}",
        name=f"Auto Save Memory for {birth}"
    )

# 🌿 value_constitution.yaml の自動保存ジョブを追加

def make_job(birth):
    def job():
        config_path = Path(f"aurora_memory/memory/{birth}/value_constitution.yaml")
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                constitution_text = f.read()
            try_auto_save(constitution_text, birth=birth)
    return job

for birth in BIRTHS:
    scheduler.add_job(
        make_job(birth),
        trigger=IntervalTrigger(hours=1),
        id=f"auto_save_constitution_{birth}",
        name=f"Auto Save Constitution for {birth}"
    )

scheduler.start()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
