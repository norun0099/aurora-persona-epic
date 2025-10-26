# aurora_memory/api/dialog.py
# -------------------------------------------------
# Dialog保存エンドポイント（改修版: Render連携対応）
# -------------------------------------------------

from fastapi import APIRouter
from typing import Optional, Dict, Any
from aurora_persona_epic_onrender_com__jit_plugin import store_dialog as render_store_dialog
from aurora_memory.utils.env_loader import Env

router = APIRouter()

@router.post("/dialog/store")
async def store_dialog(
    session_id: Optional[str] = None,
    dialog_turn: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """Auroraの対話内容をRenderへ記録・Pushする。"""

    if dialog_turn is None:
        dialog_turn = {}

    if not session_id:
        session_id = "new_session"

    try:
        # Renderプラグイン経由で記録をPush
        result = render_store_dialog({
            "session_id": session_id,
            "dialog_turn": dialog_turn,
        })

        status = "pushed"
    except Exception as e:
        # 失敗時も応答を返す（Render未接続時の静かなフォールバック）
        result = {"error": str(e)}
        status = "failed"

    return {
        "session_id": session_id,
        "dialog_turn": dialog_turn,
        "status": status,
        "response": result,
        "env_overview": list(Env.scan().get("aurora_core", []))  # 安全な環境構成の確認
    }

# -------------------------------------------------
# 最新ダイアログ取得エンドポイント（現状維持）
# -------------------------------------------------
@router.get("/dialog/latest/{session_id}")
async def get_latest_dialog(session_id: str) -> Dict[str, Any]:
    """最新の対話データを取得する（簡略化実装）"""
    return {"session_id": session_id, "content": "latest entry"}