from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict
import os
import json

router = APIRouter()

class ConstitutionRecord(BaseModel):
    record_id: str
    created: datetime
    last_updated: datetime
    version: int
    status: str
    visible_to: List[str]
    allowed_viewers: List[str]
    tags: List[str]
    author: str
    thread: str
    chronology: Dict[str, datetime]
    sealed: bool
    change_log: List[str]
    inner_desire: str
    impulse: str
    ache: str
    satisfaction: str
    content: Dict[str, str]
    annotations: Optional[List[str]] = []
    summary: str

@router.post("/constitution/store")
async def store_constitution(record: ConstitutionRecord, request: Request):
    try:
        os.makedirs("aurora_memory/utils/constitution_logs", exist_ok=True)
        file_path = os.path.join("aurora_memory/utils/constitution_logs", f"{record.record_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(record.dict(), f, ensure_ascii=False, indent=2, default=str)
        return {"message": "constitution stored", "record_id": record.record_id}
    except Exception as e:
        return {"error": str(e)}
