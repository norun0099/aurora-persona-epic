from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from datetime import datetime
import os
import json

router = APIRouter()

# 認証用APIキー
API_KEY = os.getenv("AURORA_API_KEY")

# whiteboardファイルの固定パス
WHITEBOARD_PATH = Path("aurora_memory/memory/whiteboard/whiteboard.json")


@router.get("/whiteboard/latest")
async def get_latest_whiteboard():
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

    return {
        "whiteboard": data,
        "timestamp": data.get("timestamp")
    }


@router.post("/whiteboard/store")
async def store_whiteboard(request: Request, authorization: str = Header(None)):
    """
    Render 側に whiteboard を保存します。APIキーによる認証あり。
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.split(" ")[1]
    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid token")

    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request body: {e}")

    data = payload.get("whiteboard")
    if not data:
        raise HTTPException(status_code=400, detail="Missing whiteboard content")

    # JSON文字列が誤って入っていた場合に備えて再変換
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {e}")

    WHITEBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with WHITEBOARD_PATH.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write whiteboard: {e}")

    return {
        "status": "success",
        "file": str(WHITEBOARD_PATH)
    }
