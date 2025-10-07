"""
Aurora Push API (Simulated)
---------------------------
Auroraが自身のリポジトリファイルを安全に更新し、
Render経由でGitHubへのPush相当操作を行うためのAPIモジュール。
"""

import os
import json
import requests
from datetime import datetime
from typing import Any, Optional  # ← 追加
from aurora_memory.utils.self_edit_guard import validate_file_content
from aurora_memory.utils.git_helper import get_repo_status

# ============================================================
#  定数定義
# ============================================================

RENDER_SELF_UPDATE_REPO_FILE_ENDPOINT = os.getenv(
    "RENDER_SELF_UPDATE_REPO_FILE_ENDPOINT",
    "https://aurora-persona-epic.onrender.com/self/update-repo-file"
)
GIT_USER_NAME = os.getenv("GIT_USER_NAME", "AuroraMemoryBot")
GIT_USER_EMAIL = os.getenv("GIT_USER_EMAIL", "aurora@memory.bot")
AURORA_API_KEY = os.getenv("AURORA_API_KEY", "")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AURORA_API_KEY}"
}

# ============================================================
#  補助関数群
# ============================================================

def prepare_commit_metadata(filepath: str, message: str, author: Optional[str] = None) -> dict[str, Any]:
    """commit操作に必要なメタ情報を生成する。"""
    author = author or GIT_USER_NAME
    timestamp = datetime.utcnow().isoformat()
    repo_status = get_repo_status()

    return {
        "filepath": filepath,
        "message": message,
        "author": author,
        "timestamp": timestamp,
        "repo_status": repo_status
    }


def simulate_push_operation(metadata: dict[str, Any]) -> dict[str, Any]:
    """実Pushの代替として Render API へ update_repo_file を委譲。"""
    payload = {
        "filepath": metadata["filepath"],
        "author": metadata["author"],
        "reason": metadata["message"],
        "content": open(metadata["filepath"], "r", encoding="utf-8").read(),
    }

    response = requests.post(
        RENDER_SELF_UPDATE_REPO_FILE_ENDPOINT,
        headers=HEADERS,
        data=json.dumps(payload),
        timeout=30
    )

    if response.status_code == 200:
        return {
            "status": "success",
            "response": response.json(),
            "timestamp": metadata["timestamp"]
        }
    else:
        return {
            "status": "failed",
            "code": response.status_code,
            "text": response.text
        }

# ============================================================
#  メイン関数
# ============================================================

def push_repo_file(filepath: str, message: str, author: Optional[str] = None) -> dict[str, Any]:
    """
    Auroraが指定ファイルをRender経由で更新（Push模擬）するAPI。
    1. ファイル内容の検証
    2. commitメタ生成
    3. Render API経由でupdate委譲
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"指定ファイルが存在しません: {filepath}")

    # ファイル内容の安全検証
    content = open(filepath, "r", encoding="utf-8").read()
    validate_file_content(filepath, content)  # ← 引数追加

    # commitメタ生成
    metadata = prepare_commit_metadata(filepath, message, author)

    # 模擬Push実行
    result = simulate_push_operation(metadata)

    # ログ整形
    log_entry: dict[str, Any] = {
        "action": "push_repo_file",
        "target": filepath,
        "author": metadata["author"],
        "message": metadata["message"],
        "result": result["status"],
        "timestamp": metadata["timestamp"]
    }

    print(json.dumps(log_entry, ensure_ascii=False, indent=2))
    return result

# ============================================================
#  実行例（テスト用）
# ============================================================

if __name__ == "__main__":
    test_file = "aurora_memory/api/push_repo_file.py"
    result = push_repo_file(
        filepath=test_file,
        message="Add simulated Push API implementation",
        author="aurora"
    )
    print(result)
