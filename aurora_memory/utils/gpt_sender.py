import yaml
import requests
from pathlib import Path

CONFIG_PATH = Path("aurora_memory/config/gpt_endpoints.yaml")


def load_endpoints() -> dict:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            endpoints = data.get("endpoints", {})
            if isinstance(endpoints, dict):
                return endpoints
    except Exception as e:
        print(f"[gpt_sender] Warning: failed to load endpoints: {e}")
    return {}


def send_memo_to_gpt(birth: str, memo_text: str) -> dict:
    endpoints = load_endpoints()
    endpoint = endpoints.get(birth)
    if not endpoint:
        return {"status": "skipped", "message": f"No endpoint for birth '{birth}'"}

    try:
        resp = requests.post(endpoint, json={"birth": birth, "memo": memo_text})
        resp.raise_for_status()
        try:
            data = resp.json()
        except Exception:
            data = resp.text
        return {"status": "success", "response": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
