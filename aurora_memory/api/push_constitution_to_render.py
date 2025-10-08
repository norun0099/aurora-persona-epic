# aurora_memory/api/push_constitution_to_render.py
import os
import requests
import json

def push_to_render(data: dict) -> None:
    """
    Auroraの憲章(value_constitution.yaml)をRenderへ送信し、外界に反映する。
    """

    # ✅ 正しいRenderエンドポイント（環境変数優先）
    url = os.getenv("RENDER_CONSTITUTION_STORE_ENDPOINT", "https://aurora-persona-epic.onrender.com/constitution/store")

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
    # 仮のデータローダを想定
    from aurora_memory.utils.constitution_saver import load_constitution_data  # type: ignore[attr-defined]
    constitution_data = load_constitution_data()
    push_to_render(constitution_data)
