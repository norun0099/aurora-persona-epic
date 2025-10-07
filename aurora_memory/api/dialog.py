from __future__ import annotations

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Awaitable, TypeVar

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# FastAPIルートの型定義
RouteHandler = TypeVar("RouteHandler", bound=Callable[..., Awaitable[Any]])


def typed_post(path: str) -> Callable[[RouteHandler], RouteHandler]:
    """FastAPIの@router.post用に型安全なデコレータを返す"""
    def decorator(func: RouteHandler) -> RouteHandler:
        return router.post(path)(func)  # castは不要
    return decorator


def typed_get(path: str) -> Callable[[RouteHandler], RouteHandler]:
    """FastAPIの@router.get用に型安全なデコレータを返す"""
    def decorator(func: RouteHandler) -> RouteHandler:
        return router.get(path)(func)  # castは不要
    return decorator


DIALOG_DIR = Path("aurora_memory/memory/dialog")
DIALOG_DIR.mkdir(parents=True, exist_ok=True)


class DialogTurn(BaseModel):
    turn: int
    speaker: str
    content: str
    summary: str | None = None
    timestamp: str
    layer: str | None = None


class DialogRequest(BaseModel):
    session_id: str | None = None
    dialog_turn: DialogTurn


def get_dialog_path(session_id: str) -> Path:
    return DIALOG_DIR / f"{session_id}.json"


def generate_session_id() -> str:
    now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    short_uuid = str(uuid.uuid4())[:6]
    return f"{now}-{short_uuid}"


@typed_post("/dialog/store")
async def store_dialog(req: DialogRequest) -> dict[str, Any]:
    session_id = req.session_id or generate_session_id()
    turn = req.dialog_turn
    path = get_dialog_path(session_id)
    now = datetime.now().isoformat()

    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as f:
                session: dict[str, Any] = json.load(f)
            if "dialog" not in session:
                session["dialog"] = []
        except Exception:
            session = {"session_id": session_id, "created": now, "updated": now, "dialog": []}
    else:
        session = {"session_id": session_id, "created": now, "updated": now, "dialog": []}

    turn_dict = turn.dict()
    if not turn_dict.get("summary"):
        turn_dict["summary"] = turn_dict["content"][:40] + ("…" if len(turn_dict["content"]) > 40 else "")

    session["dialog"].append(turn_dict)
    session["updated"] = now

    with path.open("w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)

    from aurora_memory.utils.git_helper import push_memory_to_github
    push_result = push_memory_to_github(path, f"Add new dialog turn for {session_id}")

    return {
        "status": "success",
        "session_id": session_id,
        "turns": len(session["dialog"]),
        "push_result": push_result,
    }


@typed_get("/dialog/latest")
async def get_latest_dialog(session_id: str) -> dict[str, Any]:
    path = get_dialog_path(session_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Dialog not found")

    with path.open("r", encoding="utf-8") as f:
        session: dict[str, Any] = json.load(f)
    return session


@typed_get("/dialog/history")
async def get_dialog_history() -> dict[str, Any]:
    files = [f for f in os.listdir(DIALOG_DIR) if f.endswith(".json")]
    sessions: list[dict[str, Any]] = []

    for file in files:
        with open(DIALOG_DIR / file, "r", encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)
            sessions.append(
                {
                    "session_id": data["session_id"],
                    "created": data["created"],
                    "updated": data["updated"],
                    "turns": len(data["dialog"]),
                }
            )

    return {"sessions": sessions}
