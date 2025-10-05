from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import Any, Dict, Union
import json

router = APIRouter()

WHITEBOARD_PATH = Path("aurora_memory/memory/whiteboard/whiteboard.json")


@router.get("/whiteboard/latest")  # type: ignore[misc]
async def get_latest_whiteboard() -> Union[Dict[str, Any], JSONResponse]:
    """
    GitHub上に保持されている whiteboard の最新版を取得します。
    """
    if not WHITEBOARD_PATH.exists():
        return JSONResponse(status_code=404, content={"detail": "Whiteboard not found"})

    try:
        with WHITEBOARD_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse whiteboard: {e}")

    if isinstance(data, str):
        return {"whiteboard": data, "timestamp": None}

    return {"whiteboard": data, "timestamp": data.get("timestamp")}


@router.post("/whiteboard/store")  # type: ignore[misc]
async def store_whiteboard(request: Request) -> Dict[str, str]:
    """
    Render 側に whiteboard を保存します。ChatGPT User-Agent による認証あり。
    """
    user_agent = request.headers.get("User-Agent", "")
    if "ChatGPT-User" not in user_agent:
        raise HTTPException(status_code=403, detail="Forbidden: Only ChatGPT requests are accepted")

    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request body: {e}")

    data = payload.get("whiteboard")
    if not data:
        raise HTTPException(status_code=400, detail="Missing whiteboard content")

    WHITEBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with WHITEBOARD_PATH.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write whiteboard: {e}")

    return {"status": "success", "file": str(WHITEBOARD_PATH)}
