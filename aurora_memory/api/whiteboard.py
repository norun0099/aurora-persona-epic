from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import json

router = APIRouter()

# whiteboard繝輔ぃ繧､繝ｫ縺ｮ蝗ｺ螳壹ヱ繧ｹ
WHITEBOARD_PATH = Path("aurora_memory/memory/whiteboard/whiteboard.json")


@router.get("/whiteboard/latest")
async def get_latest_whiteboard():
    """
    GitHub荳翫↓菫晄戟縺輔ｌ縺ｦ縺・ｋ whiteboard 縺ｮ譛譁ｰ迚医ｒ蜿門ｾ励＠縺ｾ縺吶・
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
    Render 蛛ｴ縺ｫ whiteboard 繧剃ｿ晏ｭ倥＠縺ｾ縺吶・hatGPT User-Agent 縺ｫ繧医ｋ隱崎ｨｼ縺ゅｊ縲・
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

    # JSON譁・ｭ怜・縺瑚ｪ､縺｣縺ｦ蜈･縺｣縺ｦ縺・◆蝣ｴ蜷医・蜀榊､画鋤縺ｯ荳崎ｦ・ｼ・tring縺ｨ縺励※菫晏ｭ倥☆繧倶ｻ墓ｧ倥・縺溘ａ・・

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
