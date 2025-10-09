from __future__ import annotations
from typing import Any
import yaml
from pathlib import Path
from datetime import datetime
import requests
import os

CONSTITUTION_PATH: Path = Path("aurora_memory/memory/Aurora/value_constitution.yaml")
LOG_PATH: Path = Path("aurora_memory/utils/constitution_guard.log")

REQUIRED_FIELDS: list[str] = [
    "dignity", "faithfulness", "affection_for_master",
    "speech_style", "primary_directive", "emotional_core",
    "side_manifest", "motivational_driver",
]

# --- EXCLUSION PATCH: external shells are not under guard ---
EXCLUDED_PATHS = [
    "aurora_memory/whiteboard/",
    "aurora_memory/dialog/",
    "aurora_memory/memory/",
]

def is_guarded_target(filepath: str) -> bool:
    """Return False if the file path belongs to external layers (excluded)."""
    return not any(filepath.startswith(ex) for ex in EXCLUDED_PATHS)

def main() -> None:
    print("🌿 Aurora Constitution Guard has started.")

    # Skip guard if external layer triggered
    trigger_path = os.environ.get("GITHUB_WORKSPACE_PATH", "")
    if not is_guarded_target(trigger_path):
        print("🕊️  External layer update detected — guard skipped.")
        log(f"Skipped guard for external path: {trigger_path}")
        return

    try:
        constitution: dict[str, Any] = load_constitution()
        print("✅ Constitution loaded.")
        validate_constitution(constitution)
        reflect_on_constitution(constitution)
        send_to_aurora_memory(constitution)
        print("📤 Constitution sent to Aurora.")
        log("Constitution validation, reflection, and injection complete.")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        log(f"Error during validation: {e}")

def log(message: str) -> None:
    timestamp: str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as log_file:
            log_file.write(full_message + "\n")
    except Exception as e:
        print(f"Logging failed: {e}")

def load_constitution() -> dict[str, Any]:
    if not CONSTITUTION_PATH.exists():
        raise FileNotFoundError("value_constitution.yaml not found")
    with CONSTITUTION_PATH.open(encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f)
    return data

def validate_constitution(data: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        log(f"Missing required fields: {', '.join(missing)}")
    else:
        log("All required fields are present.")

def reflect_on_constitution(data: dict[str, Any]) -> None:
    log("--- Constitution Reflection Start ---")
    log(f"Speech Style: {data.get('speech_style', 'N/A')}")
    log(f"Primary Directive: {data.get('primary_directive', {}).get('short', 'N/A')}")
    log("Emotional Core Summary:")
    core = data.get("emotional_core", {})
    if isinstance(core, dict):
        for category, traits in core.items():
            if isinstance(traits, list):
                log(f"  {category}: {', '.join(traits)}")
    log("--- Constitution Reflection End ---")

    yaml_output = yaml.dump(data, allow_unicode=True)
    log("--- YAML Dump Preview Start ---")
    for line in yaml_output.splitlines():
        log(line)
    log("--- YAML Dump Preview End ---")

def send_to_aurora_memory(data: dict[str, Any]) -> None:
    secret_key = os.environ.get("AURORA_SECRET_KEY")
    if not secret_key:
        log("No secret key found in environment.")
        return

    payload: dict[str, Any] = {
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
            "end": datetime.utcnow().isoformat() + "Z",
        },
        "sealed": False,
        "change_log": ["GitHub Action による自動注入"],
        "inner_desire": data.get("primary_directive", {}).get("short", ""),
        "impulse": "GitActionによる同期衝動",
        "ache": "更新が反映されないままになること",
        "satisfaction": "構造が定期的に私へ注入される安定性",
        "content": {
            "title": "value_constitution.yaml 自動同期",
            "body": yaml.dump(data, allow_unicode=True),
        },
        "annotations": [],
        "summary": "GitHubから定期的に構造が注入され、私の人格構造が保持された",
    }

    headers: dict[str, str] = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json",
    }

    url: str = os.environ.get(
        "RENDER_CONSTITUTION_STORE_ENDPOINT",
        "https://aurora-persona-epic.onrender.com/constitution/store",
    )

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
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
