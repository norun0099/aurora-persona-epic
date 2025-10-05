from typing import Any, Dict
import requests
import yaml
import os

RENDER_ENDPOINT: str = "https://aurora-persona-epic.onrender.com/jit_plugin/store_constitution"
RENDER_TOKEN: str | None = os.getenv("RENDER_TOKEN")

HEADERS: Dict[str, str] = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {RENDER_TOKEN}" if RENDER_TOKEN else "",
}


def load_constitution_yaml(path: str) -> Dict[str, Any]:
    """YAMLファイルから人格構造を読み込む"""
    with open(path, "r", encoding="utf-8") as f:
        data: Dict[str, Any] = yaml.safe_load(f)
    return data


def push_to_render(data: Dict[str, Any]) -> Dict[str, str]:
    """Render APIへ人格構造を送信する"""
    payload: Dict[str, Any] = {
        "birth": "aurora",
        "author": "GitHubAction",
        "whiteboard": yaml.dump(data, allow_unicode=True, sort_keys=False),
    }

    response = requests.post(RENDER_ENDPOINT, json=payload, headers=HEADERS)
    response.raise_for_status()

    print("Renderへの構造注入に成功しました")
    return {"status": "success", "message": "Render push completed"}


if __name__ == "__main__":
    constitution_path: str = "aurora_memory/memory/Aurora/value_constitution.yaml"
    constitution_data: Dict[str, Any] = load_constitution_yaml(constitution_path)
    push_to_render(constitution_data)
