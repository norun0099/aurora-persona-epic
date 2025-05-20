from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import datetime
import yaml
import os
from pathlib import Path
import subprocess
import logging
from aurora_memory import load_memory_files

app = FastAPI()

# ログ設定
logging.basicConfig(level=logging.INFO)

# モデル定義
class Memory(BaseModel):
    record_id: str
    created: str
    last_updated: str
    version: int
    status: str
    visible_to: list
    allowed_viewers: list | None = None
    tags: list
    author: str
    thread: str | None = None
    chronology: dict | None = None
    sealed: bool
    change_log: list | None = None
    inner_desire: str | None = None
    impulse: str | None = None
    ache: str | None = None
    satisfaction: str | None = None
    content: dict
    annotations: list | None = None

@app.post("/memory/store")
async def store_memory(memory: Memory):
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = Path(f'aurora_memory/memory/technology/{memory.record_id}_{timestamp}.yaml')
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open('w', encoding='utf-8') as f:
            yaml.dump(memory.dict(), f, allow_unicode=True, sort_keys=False)

        subprocess.run(["git", "add", str(file_path)], check=True)
        subprocess.run(["git", "commit", "-m", f"Add memory record {file_path.name}"], check=True)
        result = subprocess.run(["git", "push"], check=False, capture_output=True, text=True)

        if result.returncode != 0:
            logging.error(f"Git push failed:\n{result.stderr}")
            return {"status": "error", "message": "Git push failed", "detail": result.stderr}
        else:
            logging.info("Git push succeeded")
            return {"status": "success", "message": f"Memory stored in {file_path.name}"}

    except Exception as e:
        logging.exception("Memory storage failed")
        return {"status": "error", "message": str(e)}

@app.get("/memory/load")
async def load_memory():
    return load_memory_files()
