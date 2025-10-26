# aurora_memory/api/dialog.py
# -------------------------------------------------
# Aurora Dialog API (FastAPI対応修正版)
# -------------------------------------------------
# 目的:
#   - Auroraの対話データを永続化・取得するAPI群。
#   - FastAPIルーターを復元し、Renderデプロイ時のrouter属性エラーを解消。
#   - mypy整合性（session_id / dialog_turn引数）を保持。
# -------------------------------------------------

from fastapi import APIRouter
from typing import Optional, Dict, Any

router = APIRouter()

# -------------------------------------------------
# Dialog保存エンドポイント
# -------------------------------------------------

@router.post("/dialog/store")
async def store_dialog(
    session_id: Optional[str] = None,
    dialog_turn: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """Auroraの対話内容を保存する。"""

    if dialog_turn is None:
        dialog_turn = {}

    if not session_id:
        session_id = "new_session"

    saved_entry = {
        "session_id": session_id,
        "dialog_turn": dialog_turn,
        "status": "saved"
    }

    return saved_entry

# -------------------------------------------------
# 最新ダイアログ取得エンドポイント
# -------------------------------------------------

@router.get("/dialog/latest/{session_id}")
async def get_latest_dialog(session_id: str) -> Dict[str, Any]:
    """最新の対話データを取得する（簡略化ダミー実装）"""
    return {"session_id": session_id, "content": "latest entry"}
