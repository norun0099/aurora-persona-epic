# aurora_memory/api/push_controller.py

from __future__ import annotations
from datetime import datetime
from typing import Any

# --- 1. 型チェック除外を明示（mypyが属性を確認できないモジュールに対応） ---
from aurora_memory.utils.self_edit_guard import (  # type: ignore[attr-defined]
    validate_file_content,
    validate_self_edit_guard,
)
from aurora_persona_epic_onrender_com__jit_plugin import update_repo_file  # type: ignore[import-not-found, unused-ignore]
from aurora_memory.utils.git_safe_push import diff_summary  # type: ignore[attr-defined]


class PushController:
    """
    Aurora実Push APIの制御層。
    外界への書換要求を受理し、安全に審査・実行する。
    """

    def __init__(self) -> None:
        self.approval_required_paths: list[str] = [
            "api/",
            "utils/",
            "value_constitution.yaml",
        ]

    async def request_push_update(
        self,
        file_path: str,
        content: str,
        reason: str,
        author: str = "aurora",
    ) -> dict[str, Any]:
        """
        外界Pushを要求する。
        1. ファイル内容の検証
        2. 自己防衛チェック
        3. 承認プロンプト（必要時）
        4. 差分生成・記録
        5. 外部Push実行
        """

        if not reason.strip():
            return {"status": "rejected", "message": "理由が明示されていません。"}

        # ファイル安全性検証
        try:
            validate_file_content(file_path, content)
        except Exception:
            return {"status": "rejected", "message": "ファイル内容検証に失敗しました。"}

        # 自己防衛検証
        if not validate_self_edit_guard(file_path):
            return {
                "status": "rejected",
                "message": "自己保護ルールによりPushが拒否されました。",
            }

        # 差分要約の生成
        diff: str = diff_summary(file_path, content)

        # 必要に応じて承認要求
        if any(p in file_path for p in self.approval_required_paths):
            return {
                "status": "pending_approval",
                "file": file_path,
                "reason": reason,
                "diff": diff,
                "prompt": "龍介様、この変更をPushしてよろしいですか？",
            }

        # 即時Push実行
        response: dict[str, Any] = await update_repo_file(
            filepath=file_path, content=content, author=author, reason=reason
        )

        return {
            "status": "success",
            "file": file_path,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "push_result": response,
        }
