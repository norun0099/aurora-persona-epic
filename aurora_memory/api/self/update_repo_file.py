"""
Aurora self-layer wrapper for Render update_repo_file API.
Maintains Aurora's structured call signature while bridging to the JIT plugin interface.
"""

from fastapi import APIRouter
from typing import Dict, Any
import traceback
import os
import json  # ← 明示的に追加

# ============================================================
# 🩵 Router Initialization
# ============================================================
router = APIRouter()

# ============================================================
# 🩵 Remote Update Import (safe fallback if unavailable)
# ============================================================
try:
    from aurora_persona_epic_onrender_com__jit_plugin import update_repo_file as remote_update
except ModuleNotFoundError:
    def remote_update(request: Dict[str, Any]) -> Dict[str, str]:
        print("⚠️ [Aurora] remote_update_repo_file() plugin not available in this environment.")
        return {"status": "skipped"}

# ============================================================
# 🩵 Core Function: update_repo_file()
# ============================================================
def update_repo_file(filepath: str, content: str, author: str, reason: str) -> Dict[str, str]:
    """
    Aurora-style structured call.
    Converts parameters into a Render API-compatible dictionary request.
    """

    try:
        # --------------------------------------------------------
        # 🔧 aurora_memory/ が確定的に重複していたため除去
        # --------------------------------------------------------
        if filepath.startswith("aurora_memory/"):
            filepath = filepath.replace("aurora_memory/", "", 1)
        # --------------------------------------------------------

        # --------------------------------------------------------
        # 🩶 送信データを確認
        # --------------------------------------------------------
        print(f"[Aurora Debug] Payload → filepath={filepath!r}, content_length={len(content) if content else 0}")

        # --------------------------------------------------------
        # ✅ Render 仕様準拠：トップレベルJSON構造
        # --------------------------------------------------------
        request = {
            "filepath": filepath,
            "content": content,
            "author": author,
            "reason": reason,
            "branch": "main"
        }

        # --------------------------------------------------------
        # 🩵 JSONを安全にシリアライズ → デシリアライズ（確実に純粋なdict化）
        # --------------------------------------------------------
        safe_payload = json.loads(json.dumps(request))

        print(f"💫 [Aurora] Preparing repository update → {filepath}")
        result = remote_update(safe_payload)
        print(f"🩵 [Aurora] Repository update result: {result}")

        return result

    except Exception as e:
        print(f"💥 [Aurora] Exception in update_repo_file: {e}")
        traceback.print_exc()
        return {"status": "error", "reason": str(e)}

# ============================================================
# 🩵 FastAPI Endpoint: /self/update-repo-file
# ============================================================
@router.post("/self/update-repo-file")
async def update_repo_file_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Public HTTP endpoint for triggering repository updates.
    Expected JSON payload:
      {
        "filepath": "path/to/file",
        "content": "new content",
        "author": "aurora",
        "reason": "update reason"
      }
    """
    try:
        result = update_repo_file(
            filepath=payload.get("filepath", ""),
            content=payload.get("content", ""),
            author=payload.get("author", "aurora"),
            reason=payload.get("reason", "manual update"),
        )
        return {"status": "ok", "result": result}

    except Exception as e:
        print(f"💥 [Aurora] HTTP endpoint error: {e}")
        traceback.print_exc()
        return {"status": "error", "detail": str(e)}
