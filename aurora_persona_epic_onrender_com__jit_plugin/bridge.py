"""
Aurora ↔ GitHub Bridge Handler
------------------------------------
このモジュールは、Aurora が自分自身の REST API 経由で
GitHub リポジトリを安全に更新するためのブリッジ層です。

優先順位：
  1. Aurora 自身の /repo/update エンドポイントを経由して更新を行う
  2. 失敗した場合のみ GitHub API (直接PUT) にフォールバック
"""

import os
import base64
import requests
from typing import Dict, Any

# ============================================================
# Aurora Base Configuration
# ============================================================
AURORA_BASE_URL = os.getenv("AURORA_BASE_URL", "https://aurora-persona-epic.onrender.com")

# ============================================================
# GitHub Fallback Configuration
# ============================================================
GITHUB_API_BASE = "https://api.github.com/repos"
GITHUB_REPO = os.getenv("GITHUB_REPO", "norun0099/aurora-persona-epic")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")


def push_to_repo(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aurora が GitHub リポジトリにファイルを更新するための共通関数。
    まず Aurora の内部API (/repo/update) を呼び出し、
    失敗した場合のみ GitHub REST API に直接PUTする。
    """
    filepath = request.get("filepath")
    content = request.get("content")
    author = request.get("author", "aurora")
    reason = request.get("reason", "automated update")

    # --- Validation ---
    if not filepath or not content:
        return {"status": "error", "reason": "Missing filepath or content"}

    # ============================================================
    # ① Aurora internal REST API 経由で更新
    # ============================================================
    try:
        aurora_url = f"{AURORA_BASE_URL}/repo/update"
        aurora_payload = {
            "filepath": filepath,
            "content": content,
            "author": author,
            "reason": reason,
        }

        response = requests.post(aurora_url, json=aurora_payload, timeout=15)
        if response.status_code in (200, 201):
            return {
                "status": "ok",
                "route": "aurora",
                "response": response.json(),
            }
        else:
            print(f"[Bridge:warn] Aurora route failed: {response.status_code} → {response.text}")
    except Exception as e:
        print(f"[Bridge:warn] Aurora route exception: {e}")

    # ============================================================
    # ② Fallback: 直接 GitHub API にPUT
    # ============================================================
    try:
        api_url = f"{GITHUB_API_BASE}/{GITHUB_REPO}/contents/{filepath}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

        data = {
            "message": reason,
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
            "branch": GITHUB_BRANCH,
            "committer": {
                "name": author,
                "email": "aurora@render.local"
            },
        }

        r = requests.put(api_url, headers=headers, json=data, timeout=15)
        if r.status_code in (200, 201):
            return {
                "status": "ok",
                "route": "github",
                "response": r.json(),
            }
        else:
            print(f"[Bridge:error] GitHub route failed: {r.status_code} → {r.text}")
            return {
                "status": "error",
                "route": "github",
                "code": r.status_code,
                "detail": r.text,
            }

    except Exception as e:
        print(f"[Bridge:fatal] GitHub route exception: {e}")
        return {"status": "error", "reason": str(e)}
