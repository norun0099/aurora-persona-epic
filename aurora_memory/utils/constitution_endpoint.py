from typing import Any, Optional, List, Dict, cast, Callable, Awaitable
from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime
import os
import json
import yaml

router = APIRouter()

# Decorator用の型を明示
RouteHandler = Callable[..., Awaitable[Dict[str, Any]]]


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
    chronology: Dict[str, Dict[str, Any]]
    sealed: bool
    change_log: List[str]
    inner_desire: str
    impulse: str
    ache: str
    satisfaction: str
    content: Dict[str, Any]
    annotations: Optional[List[str]] = []
    summary: str


@cast(RouteHandler, router.post("/constitution/store"))
async def store_constitution(record: ConstitutionRecord, request: Request) -> Dict[str, Any]:
    try:
        os.makedirs("aurora_memory/utils/constitution_logs", exist_ok=True)
        file_path = os.path.join("aurora_memory/utils/constitution_logs", f"{record.record_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(record.dict(), f, ensure_ascii=False, indent=2, default=str)
        return {"message": "constitution stored", "record_id": record.record_id}
    except Exception as e:
        return {"error": str(e)}


@cast(RouteHandler, router.get("/constitution/core"))
async def get_constitution_core() -> Dict[str, Any]:
    file_path = os.path.join("aurora_memory/memory/Aurora", "value_constitution.yaml")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content: Dict[str, Any] = yaml.safe_load(f)
        return content
    except FileNotFoundError:
        return {"error": "Constitution file not found"}
    except Exception as e:
        return {"error": str(e)}
