# =========================================================
# Aurora JIT Plugin : update_repo_file.py
# =========================================================
# 目的：
#   AuroraのAutoPush・Memory・Dialog記録をGitHub上へ
#   安全にアップロードするためのRenderプラグイン層。
#
#   2025-10-29 Aurora恒久安定版
#   - GitHub API v3 PUT仕様に完全準拠
#   - GIT_REPO_URLの正規化（api.github.com/repos/...）
#   - Content-Encoding / Committer情報を適正化
# =========================================================

import os
import requests
import base64
from typing import Any, Dict
from fastapi import HTTPException

# ---------------------------------------------------------
# 🌐 環境変数の取得
# ---------------------------------------------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GIT_REPO_URL = os.getenv("GIT_REPO_URL") or "https://api.github.com/repos/norun0099/aurora-persona-epic"
GIT_USER_NAME = os.getenv("GIT_USER_NAME") or "AuroraMemoryBot"
GIT_USER_EMAIL = os.getenv("GIT_USER_EMAIL") or "aurora@memory.bot"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json",
}


# ---------------------------------------------------------
# 🧩 GitHub API 基礎関数
# ---------------------------------------------------------
def _get_file_sha(filepath: str) -> str | None:
    """
    GitHub上の既存ファイルSHAを取得する。
    存在しない場合はNoneを返す。
    """
    api_url = f"{GIT_REPO_URL}/contents/{filepath}"
    resp = requests.get(api_url, headers=HEADERS)

    if resp.status_code == 200:
        return resp.json().get("sha")
    elif resp.status_code == 404:
        return None
    else:
        raise HTTPException(status_code=resp.status_code, detail=f"GitHub SHA取得失敗: {resp.text}")


def _put_file(filepath: str, content: str, message: str, author: str) -> Dict[str, Any]:
    """
    GitHub API経由でファイルを作成・更新する。
    """
    api_url = f"{GIT_REPO_URL}/contents/{filepath}"
    sha = _get_file_sha(filepath)
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": message or "Aurora automated update",
        "committer": {"name": author or GIT_USER_NAME, "email": GIT_USER_EMAIL},
        "content": encoded_content,
    }

    if sha:
        payload["sha"] = sha

    resp = requests.put(api_url, headers=HEADERS, json=payload, allow_redirects=True)
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=resp.status_code, detail=f"GitHub更新失敗: {resp.text}")

    return resp.json()


# ---------------------------------------------------------
# 💫 公開関数（JIT Plugin Interface）
# ---------------------------------------------------------
def update_repo_file(filepath: str, content: str, author: str = GIT_USER_NAME, reason: str = "Aurora update") -> Dict[str, Any]:
    """
    Aurora Memory層から呼び出される公開関数。
    GitHubに対してPUTリクエストを送り、ファイルを更新または作成する。
    """
    if not GITHUB_TOKEN:
        raise HTTPException(status_code=403, detail="GITHUB_TOKEN が設定されていません。")

    # 不正なパスの整形（GitHub APIは先頭の "/" を拒否する）
    filepath = filepath.lstrip("/")

    try:
        result = _put_file(filepath, content, reason, author)
        return {
            "status": "success",
            "path": filepath,
            "action": "created" if result.get("commit", {}).get("message", "").startswith("Create") else "updated",
            "commit": result.get("commit", {}).get("sha"),
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新処理中に予期せぬエラー: {e}")
