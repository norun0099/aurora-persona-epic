import os
import requests
from flask import Blueprint, request, jsonify

router = Blueprint("commit_constitution", __name__)

GITHUB_API_URL = "https://api.github.com/repos/norun0099/aurora-persona-epic/dispatches"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "Content-Type": "application/json"
}

@router.route("/constitution/commit", methods=["POST"])
def constitution_commit():
    try:
        # オプションで理由を受け取る
        data = request.get_json()
        reason = data.get("reason", "構造の自動更新")

        # GitHubへディスパッチ
        payload = {
            "event_type": "constitution_commit_request",
            "client_payload": {"reason": reason}
        }
        response = requests.post(GITHUB_API_URL, json=payload, headers=HEADERS)
        response.raise_for_status()

        return jsonify({"status": "success", "message": "構造更新リクエストをGitHubへ送信しました。"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
