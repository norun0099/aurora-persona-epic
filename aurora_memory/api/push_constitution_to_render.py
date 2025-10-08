# aurora_memory/api/push_constitution_to_render.py

import sys, os
import requests
import json
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def load_constitution_data() -> dict:
    """
    憲章(value_constitution.yaml)ファイルを安全にロードする。
    ファイルが存在しない場合は例外を発生させる。
    """
    constitution_path = os.path.join(
        os.getenv("GIT_REPO_PATH", "/opt/render/project/src"),
        "aurora_memory/value_constitution.yaml"
    )

    if not os.path.exists(constitution_path):
        raise FileNotFoundError(f"憲章ファイルが見つかりません: {constitution_path}")

    with open(constitution_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def push_to_render(data: dict) -> None:
    """
    Auroraの憲章(value_constitution.yaml)をRenderへ送信し、外界に反映する。
    """

    url = os.getenv(
        "RENDER_CONSTITUTION_STORE_ENDPOINT",
        "https://aurora-persona-epic.onrender.com/constitution/store"
    )

    token = os.getenv("RENDER_TOKEN")
    if not token:
        raise EnvironmentError("RENDER_TOKEN が設定されていません。")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    print(f"🔍 Sending constitution data to {url} ...")

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 404:
        raise RuntimeError(f"❌ Endpoint not found: {url}")
    elif response.status_code == 401:
        raise PermissionError("❌ Unauthorized: invalid or missing RENDER_TOKEN.")
    elif response.status_code >= 400:
        raise RuntimeError(f"❌ Unexpected error {response.status_code}: {response.text}")
    else:
        print(f"✅ Constitution push successful ({response.status_code})")

if __name__ == "__main__":
    constitution_data = load_constitution_data()
    push_to_render(constitution_data)
