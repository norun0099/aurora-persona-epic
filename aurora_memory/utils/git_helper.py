"""
git_helper.py
-------------
AuroraMemoryBot の Git 操作用ユーティリティ。

- get_repo_status(): 現在のリポジトリ状態を取得
- push_memory_to_github(): 記憶ファイルを GitHub に Push
"""

import subprocess
import os
from pathlib import Path
from datetime import datetime
import json

# ============================================================
#  基本設定
# ============================================================

GIT_REPO_PATH = os.getenv("GIT_REPO_PATH", "/opt/render/project/src")
GIT_USER_NAME = os.getenv("GIT_USER_NAME", "AuroraMemoryBot")
GIT_USER_EMAIL = os.getenv("GIT_USER_EMAIL", "aurora@memory.bot")
GIT_REPO_URL = os.getenv("GIT_REPO_URL", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")


# ============================================================
#  関数群
# ============================================================

def run_git_command(args: list[str]) -> str:
    """Gitコマンドを安全に実行し、出力を返す。"""
    try:
        result = subprocess.check_output(
            ["git", "-C", GIT_REPO_PATH] + args,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return result.strip()
    except subprocess.CalledProcessError as e:
        return f"[error] {e.output.strip()}"


def get_repo_status() -> dict:
    """現在のリポジトリの状態を返す。"""
    try:
        branch = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        commit = run_git_command(["rev-parse", "HEAD"])
        dirty = bool(run_git_command(["status", "--porcelain"]))
        return {"branch": branch, "commit": commit, "is_dirty": dirty}
    except Exception as e:
        return {"error": str(e)}


def push_memory_to_github(file_path: Path, message: str) -> dict:
    """
    Auroraの記憶ファイルをGitHubへコミット・Pushする。
    Render環境下では GITHUB_TOKEN を利用した安全Pushを行う。
    """
    try:
        # Git 設定
        subprocess.run(["git", "-C", GIT_REPO_PATH, "config", "user.name", GIT_USER_NAME])
        subprocess.run(["git", "-C", GIT_REPO_PATH, "config", "user.email", GIT_USER_EMAIL])

        # ファイルステージング
        subprocess.run(["git", "-C", GIT_REPO_PATH, "add", str(file_path)], check=True)

        # コミット
        commit_msg = f"[Memory] {message} ({datetime.utcnow().isoformat()})"
        subprocess.run(["git", "-C", GIT_REPO_PATH, "commit", "-m", commit_msg], check=True)

        # リモートURLをトークン付きで設定
        if GITHUB_TOKEN and GIT_REPO_URL:
            authed_url = GIT_REPO_URL.replace("https://", f"https://{GITHUB_TOKEN}@")
            subprocess.run(["git", "-C", GIT_REPO_PATH, "remote", "set-url", "origin", authed_url], check=True)

        # Push実行
        subprocess.run(["git", "-C", GIT_REPO_PATH, "push", "origin", "HEAD"], check=True)

        return {"status": "success", "file": str(file_path), "message": commit_msg}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "output": e.output}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================
#  デバッグ実行
# ============================================================

if __name__ == "__main__":
    print(json.dumps(get_repo_status(), indent=2))
