from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import json

router = APIRouter()

# whiteboardファイルの固定パス
WHITEBOARD_PATH = Path("aurora_memory/memory/whiteboard/whiteboard.json")


@router.get("/whiteboard/latest")
async def get_latest_whiteboard():
    """
    GitHub上に保持されてぁE�� whiteboard の最新版を取得します、E
    """
    if not WHITEBOARD_PATH.exists():
        return JSONResponse(status_code=404, content={"detail": "Whiteboard not found"})

    try:
        with WHITEBOARD_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse whiteboard: {e}")

    if isinstance(data, str):
        return {
            "whiteboard": data,
            "timestamp": None
        }

    return {
        "whiteboard": data,
        "timestamp": data.get("timestamp")
    }


@router.post("/whiteboard/store")
async def store_whiteboard(request: Request):
    """
    Render 側に whiteboard を保存します、EhatGPT User-Agent による認証あり、E
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

    # JSON斁E���Eが誤って入ってぁE��場合�E再変換は不要E��Etringとして保存する仕様�Eため�E�E

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
