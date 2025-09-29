import requests
import yaml
import os

RENDER_ENDPOINT = "https://aurora-persona-epic.onrender.com/jit_plugin/store_constitution"
RENDER_TOKEN = os.getenv("RENDER_TOKEN")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {RENDER_TOKEN}"
}


def load_constitution_yaml(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def push_to_render(data: dict) -> None:
    payload = {
        "birth": "aurora",
        "author": "GitHubAction",
    }
    payload.update({"whiteboard": yaml.dump(data, allow_unicode=True, sort_keys=False)})

    response = requests.post(RENDER_ENDPOINT, json=payload, headers=HEADERS)
    response.raise_for_status()
    print("Renderへの構造注入に成功しました。")


if __name__ == "__main__":
    constitution_path = "aurora_memory/memory/Aurora/value_constitution.yaml"
    constitution_data = load_constitution_yaml(constitution_path)
    push_to_render(constitution_data)
