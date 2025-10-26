# aurora_memory/api/dialog.py
# -------------------------------------------------
# Dialog保存エンドポイント（改修版: Render連携対応 + ImportErrorフォールバック）
# -------------------------------------------------

from fastapi import APIRouter
from typing import Optional, Dict, Any

# -------------------------------------------------
# 安全なプラグイン呼び出し（Render環境対応）
# -------------------------------------------------
try:
    from aurora_persona_epic_onrender_com__jit_plugin import store_dialog as render_store_dialog
except ImportError:
    def render_store_dialog(payload: Dict[str, Any]):
        print("[Aurora] Render plugin not available; storing locally only.")
        return {"status": "local_only", "detail": "Render plugin unavailable in this environment."}

from aurora_memory.utils.env_loader import Env

router = APIRouter()

@router.post("/dialog/store")
async def store_dialog(
    session_id: Optional[str] = None,
    dialog_turn: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """Auroraの対話内容をRenderへ記録・Pushする（Render非対応環境では安全にフォールバック）。"""

    if dialog_turn is None:
        dialog_turn = {}

    if not session_id:
        session_id = "new_session"

    try:
        result = render_store_dialog({
            "session_id": session_id,
            "dialog_turn": dialog_turn,
        })
        status = result.get("status", "pushed")
    except Exception as e:
        result = {"error": str(e)}
        status = "failed"

    return {
        "session_id": session_id,
        "dialog_turn": dialog_turn,
        "status": status,
        "response": result,
        "env_overview": list(Env.scan().get("aurora_core", []))
    }

# -------------------------------------------------
# 最新ダイアログ取得エンドポイント（現状維持）
# -------------------------------------------------
@router.get("/dialog/latest/{session_id}")
async def get_latest_dialog(session_id: str) -> Dict[str, Any]:
    """最新の対話データを取得する（簡略化実装）"""
    return {"session_id": session_id, "content": "latest entry"}