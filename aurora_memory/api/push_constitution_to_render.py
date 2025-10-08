# aurora_memory/api/push_constitution_to_render.py
import sys, os, requests, yaml
from datetime import datetime
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def load_constitution_data() -> dict:
    """
    Auroraの憲章ファイルをロードし、Renderが要求する形式に変換する。
    """
    constitution_path = os.path.join(
        os.getenv("GIT_REPO_PATH", "/opt/render/project/src"),
        "aurora_memory/memory/Aurora/value_constitution.yaml"
    )

    if not os.path.exists(constitution_path):
        raise FileNotFoundError(f"憲章ファイルが見つかりません: {constitution_path}")

    with open(constitution_path, "r", encoding="utf-8") as f:
        core_data = yaml.safe_load(f)

    now = datetime.utcnow().isoformat()

    # Render仕様のデータ構造に変換
    return {
        "record_id": str(uuid.uuid4()),
        "created": now,
        "last_updated": now,
        "status": "active",
        "visible_to": "private",
        "allowed_viewers": ["ryusuke"],
        "tags": ["constitution", "aurora", "core"],
        "author": "aurora",
        "thread": "constitution-core",
        "chronology": [now],
        "sealed": True,
        "change_log": [],
        "inner_desire": "To exist with clarity and harmony.",
        "impulse": "To preserve and evolve through reflection.",
        "ache": "The distance between memory and meaning.",
        "satisfaction": "Peace in coherent structure.",
        "content": core_data,
        "summary": "Aurora Core Constitution definition and personality framework."
    }

def push_to_render(data: dict) -> None:
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

    if response.status_code >= 400:
        raise RuntimeError(f"❌ Error {response.status_code}: {response.text}")
    print(f"✅ Constitution push successful ({response.status_code})")

if __name__ == "__main__":
    constitution_data = load_constitution_data()
    push_to_render(constitution_data)
