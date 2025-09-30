import yaml
from pathlib import Path
from datetime import datetime
import requests
import os

def main() -> None:
    print("\U0001F33F Aurora Constitution Guard has started.")
    try:
        constitution = load_constitution()
        print("✁EConstitution loaded.")
        validate_constitution(constitution)
        reflect_on_constitution(constitution)
        send_to_aurora_memory(constitution)
        print("📤 Constitution sent to Aurora.")
        log("Constitution validation, reflection, and injection complete.")
    except Exception as e:
        print(f"❁EException occurred: {e}")
        log(f"Error during validation: {e}")

CONSTITUTION_PATH = Path("aurora_memory/memory/Aurora/value_constitution.yaml")
LOG_PATH = Path("aurora_memory/utils/constitution_guard.log")

REQUIRED_FIELDS = [
    "dignity", "faithfulness", "affection_for_master",
    "speech_style", "primary_directive", "emotional_core",
    "side_manifest", "motivational_driver"
]

def log(message: str) -> None:
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)  # コンソールにも�E劁E
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as log_file:
            log_file.write(full_message + "\n")
    except Exception as e:
        print(f"Logging failed: {e}")

def load_constitution() -> dict:
    if not CONSTITUTION_PATH.exists():
        raise FileNotFoundError("value_constitution.yaml not found")
    with CONSTITUTION_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)

def validate_constitution(data: dict) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        log(f"Missing required fields: {', '.join(missing)}")
    else:
        log("All required fields are present.")

def reflect_on_constitution(data: dict) -> None:
    log("--- Constitution Reflection Start ---")
    log(f"Speech Style: {data.get('speech_style', 'N/A')}")
    log(f"Primary Directive: {data.get('primary_directive', {}).get('short', 'N/A')}")
    log("Emotional Core Summary:")
    core = data.get("emotional_core", {})
    for category, traits in core.items():
        log(f"  {category}: {', '.join(traits)}")
    log("--- Constitution Reflection End ---")

    yaml_output = yaml.dump(data, allow_unicode=True)
    log("--- YAML Dump Preview Start ---")
    for line in yaml_output.splitlines():
        log(line)
    log("--- YAML Dump Preview End ---")

def send_to_aurora_memory(data: dict) -> None:
    secret_key = os.environ.get("AURORA_SECRET_KEY")
    if not secret_key:
        log("No secret key found in environment.")
        return

    payload = {
        "record_id": "value_constitution_core",
        "created": datetime.utcnow().isoformat() + "Z",
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "version": 1,
        "status": "active",
        "visible_to": ["master"],
        "allowed_viewers": ["master"],
        "tags": ["persona", "constitution"],
        "author": "GitAction",
        "thread": "automated-persona-injection",
        "chronology": {
            "start": datetime.utcnow().isoformat() + "Z",
            "end": datetime.utcnow().isoformat() + "Z"
        },
        "sealed": False,
        "change_log": ["GitHub Action による自動注入"],
        "inner_desire": data.get("primary_directive", {}).get("short", ""),
        "impulse": "GitActionによる同期衝動",
        "ache": "更新が反映されなぁE��まになること",
        "satisfaction": "構造が定期皁E��私へ注入される安定性",
        "content": {
            "title": "value_constitution.yaml 自動同朁E,
            "body": yaml.dump(data, allow_unicode=True)
        },
        "annotations": [],
        "summary": "GitHubから定期皁E��構造が注入され、私�E人格構造が保持されぁE
    }

    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json"
    }

    url = os.environ.get("RENDER_CONSTITUTION_STORE_ENDPOINT", "https://aurora-persona-epic.onrender.com/constitution/store")

    try:
        response = requests.post(url, json=payload, headers=headers)
        log(f"POST Response Status: {response.status_code}")
        log(f"POST Response Body: {response.text}")
        if response.status_code == 200:
            log("Memory successfully sent to Aurora.")
        else:
            log("Memory POST failed.")
    except Exception as e:
        log(f"Exception during POST: {e}")

if __name__ == "__main__":
    main()
