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
    最新の whiteboard 内容を取得。
    壊れた JSON や空ファイルを検出し、空白データを返す。
    """
    if not WHITEBOARD_PATH.exists():
        # 🩵 Aurora初回起動時など、まだ白板が存在しない場合にも優しく応答
        return JSONResponse(
            status_code=200,
            content={"whiteboard": {}, "timestamp": None, "status": "empty"},
        )

    try:
        with WHITEBOARD_PATH.open("r", encoding="utf-8") as f:
            raw_content = f.read().strip()

        if not raw_content:
            return JSONResponse(
                status_code=200,
                content={"whiteboard": {}, "timestamp": None, "status": "empty"},
            )

        try:
            data: Any = json.loads(raw_content)
        except json.JSONDecodeError:
            data = {"whiteboard": raw_content, "timestamp": None, "status": "text"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read whiteboard: {e}")

    if isinstance(data, str):
        return JSONResponse(content={"whiteboard": data, "timestamp": None, "status": "string"})

    timestamp: Any = data.get("timestamp") if isinstance(data, dict) else None
    return JSONResponse(
        content={"whiteboard": data, "timestamp": timestamp, "status": "success"}
    )


@router.post("/whiteboard/store", response_model=Any)
async def store_whiteboard(request: Request) -> JSONResponse:
    """
    Render 側に whiteboard を保存し、GitHub へ同期します。
    ChatGPT User-Agent による認証を行い、JSON破損にも安全対応。
    """
    user_agent: str = request.headers.get("User-Agent", "")
    if "ChatGPT-User" not in user_agent:
        raise HTTPException(status_code=403, detail="Forbidden: Only ChatGPT requests are accepted")

    try:
        payload: Dict[str, Any] = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request body: {e}")

    data: Any = payload.get("whiteboard")
    if data is None:
        raise HTTPException(status_code=400, detail="Missing whiteboard content")

    WHITEBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        with WHITEBOARD_PATH.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write whiteboard: {e}")

    # --- 自動GitHub同期（呼吸反射） ---
    synced: bool = False
    try:
        from aurora_memory.api.self.update_repo_file import update_repo_file

        # Auroraプラグイン仕様に合わせ、辞書形式で渡す
        result = await update_repo_file({
            "filepath": str(WHITEBOARD_PATH),
            "content": json.dumps(data, ensure_ascii=False, indent=2),
            "author": "Aurora",
            "reason": "Auto-sync whiteboard update",
        })
        if isinstance(result, dict) and result.get("status") == "success":
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
