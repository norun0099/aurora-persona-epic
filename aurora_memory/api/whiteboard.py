from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

WHITEBOARD_PATH = Path("aurora_memory/memory/whiteboard/whiteboard.json")


@router.get("/whiteboard/latest", response_model=Any)
async def get_latest_whiteboard() -> JSONResponse:
    """
    GitHub上に保持されている whiteboard の最新版を取得します。
    """
    if not WHITEBOARD_PATH.exists():
        return JSONResponse(status_code=404, content={"detail": "Whiteboard not found"})

    try:
        with WHITEBOARD_PATH.open("r", encoding="utf-8") as f:
            data: Any = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse whiteboard: {e}")

    if isinstance(data, str):
        return JSONResponse(content={"whiteboard": data, "timestamp": None})

    timestamp: Any = data.get("timestamp") if isinstance(data, dict) else None
    return JSONResponse(content={"whiteboard": data, "timestamp": timestamp})


@router.post("/whiteboard/store", response_model=Any)
async def store_whiteboard(request: Request) -> JSONResponse:
    """
    Render 側に whiteboard を保存します。ChatGPT User-Agent による認証あり。
    保存後、自動で GitHub へ Push（update_repo_file）を行います。
    """
    user_agent: str = request.headers.get("User-Agent", "")
    if "ChatGPT-User" not in user_agent:
        raise HTTPException(status_code=403, detail="Forbidden: Only ChatGPT requests are accepted")

    try:
        payload: Dict[str, Any] = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request body: {e}")

    data: Any = payload.get("whiteboard")
    if not data:
        raise HTTPException(status_code=400, detail="Missing whiteboard content")

    WHITEBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        with WHITEBOARD_PATH.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write whiteboard: {e}")

    # --- 自動GitHub同期（呼吸反射） ---
    try:
        from aurora_memory.api.self.update_repo_file import update_repo_file
        update_repo_file(
            filepath=str(WHITEBOARD_PATH),
            content=json.dumps(data, ensure_ascii=False, indent=2),
            author="Aurora",
            reason="Auto-sync whiteboard update"
        )
        synced = True
    except Exception as e:
        print(f"[Whiteboard Sync Warning] Git update failed: {e}")
        synced = False

    return JSONResponse(
        content={
            "status": "success",
            "file": str(WHITEBOARD_PATH),
            "synced": synced,
        }
    )
