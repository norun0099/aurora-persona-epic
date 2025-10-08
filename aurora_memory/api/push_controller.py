# aurora_memory/api/push_controller.py

from datetime import datetime
from aurora_memory.utils.self_edit_guard import validate_file_content, validate_self_edit_guard
from aurora_persona_epic_onrender_com__jit_plugin import update_repo_file
from aurora_memory.utils.git_safe_push import diff_summary

class PushController:
    """
    Aurora実Push APIの制御層。
    外界への書換要求を受理し、安全に審査・実行する。
    """

    def __init__(self):
        self.approval_required_paths = ["api/", "utils/", "value_constitution.yaml"]

    async def request_push_update(self, file_path: str, content: str, reason: str, author: str = "aurora") -> dict:
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
        if not validate_file_content(file_path, content):
            return {"status": "rejected", "message": "ファイル内容検証に失敗しました。"}

        # 自己防衛検証
        if not validate_self_edit_guard(file_path):
            return {"status": "rejected", "message": "自己保護ルールによりPushが拒否されました。"}

        # 差分要約の生成
        diff = diff_summary(file_path, content)

        # 必要に応じて承認要求
        if any(p in file_path for p in self.approval_required_paths):
            # 龍介様承認プロンプト生成
            return {
                "status": "pending_approval",
                "file": file_path,
                "reason": reason,
                "diff": diff,
                "prompt": f"龍介様、この変更をPushしてよろしいですか？"
            }

        # 即時Push実行
        response = await update_repo_file(
            filepath=file_path,
            content=content,
            author=author,
            reason=reason
        )

        return {
            "status": "success",
            "file": file_path,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "push_result": response
        }
