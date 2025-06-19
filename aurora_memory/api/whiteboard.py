from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from datetime import datetime
import os
import json

router = APIRouter()

API_KEY = os.getenv("AURORA_API_KEY")

@router.get("/whiteboard/latest")
async def get_latest_whiteboard(birth: str = "Aurora"):
    wb_path = Path(f"aurora_memory/memory/{birth}/whiteboard.json")
    if not wb_path.exists():
        return JSONResponse(status_code=404, content={"detail": "Whiteboard not found"})

    with wb_path.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse whiteboard: {e}")

    return {
        "whiteboard": data,
        "timestamp": data.get("timestamp", None)
    }

@router.post("/whiteboard/store")
async def store_whiteboard(request: Request, authorization: str = Header(None), birth: str = "Aurora"):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.split(" ")[1]
    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid token")

    payload = await request.json()
    data = payload.get("whiteboard")
    if not data:
        raise HTTPException(status_code=400, detail="Missing whiteboard content")

    # 文字列で送られてきた場合、JSONとして解釈を試みる
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {e}")

    wb_path = Path(f"aurora_memory/memory/{birth}/whiteboard.json")
    wb_path.parent.mkdir(parents=True, exist_ok=True)

    with wb_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {"status": "success", "file": str(wb_path)}
