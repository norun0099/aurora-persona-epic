from fastapi import APIRouter, Request, Header, HTTPException
from pathlib import Path
from fastapi.responses import JSONResponse
from datetime import datetime
import os

router = APIRouter()

# 認証（必要であれば環境変数）
API_KEY = os.getenv("AURORA_API_KEY")

@router.get("/whiteboard/latest")
async def get_latest_whiteboard(birth: str = "Aurora"):
    wb_path = Path(f"aurora_memory/memory/{birth}/whiteboard.yaml")
    if not wb_path.exists():
        return JSONResponse(status_code=404, content={"detail": "Whiteboard not found"})

    with wb_path.open("r", encoding="utf-8") as f:
        content = f.read()

    timestamp = datetime.utcfromtimestamp(wb_path.stat().st_mtime).isoformat() + "Z"
    return {
        "whiteboard": content,
        "timestamp": timestamp
    }

@router.post("/whiteboard/store")
async def store_whiteboard(request: Request, authorization: str = Header(None), birth: str = "Aurora"):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.split(" ")[1]
    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid token")

    data = await request.json()
    notes = data.get("whiteboard", "")

    wb_path = Path(f"aurora_memory/memory/{birth}/whiteboard.yaml")
    wb_path.parent.mkdir(parents=True, exist_ok=True)

    with wb_path.open("w", encoding="utf-8") as f:
        f.write(notes)

    return {"status": "success", "file": str(wb_path)}
