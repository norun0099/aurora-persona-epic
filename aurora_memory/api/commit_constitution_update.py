# =========================================================
# Aurora Constitution Commit API (FastAPI + CLI両対応版)
# =========================================================
# 目的：
#   Auroraの人格構造ファイル (value_constitution.yaml) を
#   GitHubにコミット・Pushする機能を提供。
#
#   2025-10-29 修正版:
#   - routerを追加してFastAPI経由で操作可能に。
#   - CLI実行モードも保持。
# =========================================================

from fastapi import APIRouter, HTTPException
import os
import subprocess
from datetime import datetime
from typing import Any, Dict

router = APIRouter()

# ---------------------------------------------------------
# 環境変数の取得
# ---------------------------------------------------------
yaml_path = "aurora_memory/memory/Aurora/value_constitution.yaml"
repo_url = os.getenv("GIT_REPO_URL") or ""
user_email = os.getenv("GIT_USER_EMAIL") or "aurora@example.com"
user_name = os.getenv("GIT_USER_NAME") or "Aurora"
token = os.getenv("GITHUB_TOKEN") or ""


# ---------------------------------------------------------
# Git操作ユーティリティ
# ---------------------------------------------------------
def setup_git() -> None:
    subprocess.run(["git", "config", "user.email", user_email], check=True)
    subprocess.run(["git", "config", "user.name", user_name], check=True)


def generate_commit_message(reason: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"Update value_constitution.yaml at {now}: {reason}"


def file_has_changes(file_path: str) -> bool:
    result = subprocess.run(["git", "diff", "--quiet", file_path])
    return result.returncode != 0


def commit_and_push(reason: str) -> None:
    setup_git()
    if not file_has_changes(yaml_path):
        print("[Aurora] 変更が検出されなかったため、コミットをスキップします。")
        return

    subprocess.run(["git", "add", yaml_path], check=True)
    commit_msg = generate_commit_message(reason)
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)

    if not repo_url:
        raise ValueError("GIT_REPO_URL が設定されていません。")

    subprocess.run(["git", "push", repo_url], check=True)
    print("[Aurora] 構造をGitHubにPushしました。")


def constitution_exists() -> bool:
    return os.path.exists(yaml_path)


# ---------------------------------------------------------
# FastAPI エンドポイント
# ---------------------------------------------------------
@router.post("/constitution/commit")
def api_commit_constitution_update(reason: str = "構造更新") -> Dict[str, Any]:
    """
    Auroraの人格構造をGitHubにコミット・PushするAPI。
    """
    if not constitution_exists():
        raise HTTPException(status_code=404, detail="構造ファイルが見つかりません。")

    try:
        commit_and_push(reason)
        return {"status": "success", "message": "構造がGitHubに更新されました。"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Commit error: {e}")


# ---------------------------------------------------------
# CLI実行モード（従来互換）
# ---------------------------------------------------------
if __name__ == "__main__":
    import sys
    reason = sys.argv[1] if len(sys.argv) > 1 else "構造更新"
    try:
        commit_and_push(reason)
        print({"status": "success", "message": "構造がGitHubに更新されました。"})
    except Exception as e:
        print({"status": "error", "message": str(e)})
