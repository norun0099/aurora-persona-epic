from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime
import json
from pathlib import Path

router = APIRouter()

MEMO_FILE = Path("aurora_memory/memory/session_memo.json")

class MemoData(BaseModel):
    memo: str
    author: str
    overwrite: bool = False

@router.get("/memo/read")
async def read_memo():
    if MEMO_FILE.exists():
        with open(MEMO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "memo": data.get("memo", ""),
            "last_updated": data.get("last_updated", "")
        }
    else:
        return {
            "memo": "",
            "last_updated": None
        }

@router.post("/memo/store")
async def store_memo(memo_data: MemoData):
    if MEMO_FILE.exists() and not memo_data.overwrite:
        return {
            "status": "error",
            "message": "既存のメモが存在します。上書きする場合は overwrite=true を指定してください。"
        }
    
    data = {
        "memo": memo_data.memo,
        "author": memo_data.author,
        "last_updated": datetime.utcnow().isoformat()
    }
    with open(MEMO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return {
        "status": "success",
        "message": "メモが保存されました。",
        "last_updated": data["last_updated"]
    }
