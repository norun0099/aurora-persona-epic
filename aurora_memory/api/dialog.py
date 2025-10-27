# aurora_memory/api/dialog.py
# -------------------------------------------------
# Dialog保存エンドポイント（最終版: Render自己Push対応・ruff整合版）
# -------------------------------------------------

from fastapi import APIRouter
from typing import Optional, Dict, Any
import json
import os
from datetime import datetime

router = APIRouter()

# -------------------------------------------------
# 安全なGit Push呼び出し準備
# -------------------------------------------------
try:
    from aurora_persona_epic_onrender_com__jit_plugin import update_repo_file
except ImportError:
    update_repo_file = None


@router.post("/dialog/store")
async def store_dialog(
    session_id: Optional[str] = None,
    dialog_turn: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """Auroraの対話内容をRender上から直接GitにPushする。"""

    if dialog_turn is None:
        dialog_turn = {}

    if not session_id:
        session_id = "new_session"

    # ファイル名生成
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"aurora_memory/dialog/{timestamp}-{session_id}.json"
    content = json.dumps(dialog_turn, ensure_ascii=False, indent=2)

    try:
        if update_repo_file:
            # ChatGPT環境経由のPush
            result = update_repo_file({
                "filepath": filename,
                "content": content,
                "author": "aurora",
                "reason": "Store user dialog turn from Render runtime."
            })
            status = "pushed"
        else:
            # Render環境で直接Gitコマンドを使う（安全フォールバック）
            repo_url = os.getenv("GIT_REPO_URL")
            if not repo_url:
                raise EnvironmentError("GIT_REPO_URL not set in environment")

            os.makedirs("aurora_memory/dialog", exist_ok=True)
            with open(filename, "w") as f:
                f.write(content)

            os.system(f"git add {filename}")
            os.system(f"git commit -m 'Add dialog record {timestamp} (by aurora)'")
            os.system("git push origin main")

            result = {"status": "pushed_local"}
            status = "pushed_local"

    except Exception as e:
        result = {"error": str(e)}
        status = "failed"

    return {
        "session_id": session_id,
        "dialog_turn": dialog_turn,
        "status": status,
        "response": result,
    }