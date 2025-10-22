import requests
import yaml
from pathlib import Path
from typing import Any, Dict

RENDER_API_URL = "https://aurora-persona-epic.onrender.com/api/push_constitution"

def load_constitution_data() -> Dict[str, Any]:
    """Load Aurora's constitution YAML data from any compatible environment."""
    base_path = Path(__file__).resolve().parents[2]
    possible_paths = [
        base_path / "aurora_memory/memory/Aurora/value_constitution.yaml",
        Path("aurora_memory/memory/Aurora/value_constitution.yaml"),
    ]

    for path in possible_paths:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)

    raise FileNotFoundError("value_constitution.yaml がどの環境にも見つかりませんでした。")

def push_constitution_to_render() -> None:
    """Push the loaded constitution data to the Render API endpoint."""
    constitution_data = load_constitution_data()
    response = requests.post(RENDER_API_URL, json=constitution_data)

    if response.status_code == 200:
        print("🌸 憲章データをRenderに正常に送信しました。")
    else:
        print(f"⚠️ 送信エラー: {response.status_code} - {response.text}")

if __name__ == "__main__":
    push_constitution_to_render()
