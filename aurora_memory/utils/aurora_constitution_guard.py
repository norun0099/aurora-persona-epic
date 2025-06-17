import yaml
from pathlib import Path
from datetime import datetime
import requests
import os

CONSTITUTION_PATH = Path("aurora_memory/memory/Aurora/value_constitution.yaml")
LOG_PATH = Path("aurora_memory/utils/constitution_guard.log")

REQUIRED_FIELDS = [
    "dignity", "faithfulness", "affection_for_master",
    "speech_style", "primary_directive", "emotional_core",
    "side_manifest", "motivational_driver"
]

def log(message: str):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

def load_constitution() -> dict:
    if not CONSTITUTION_PATH.exists():
        raise FileNotFoundError("value_constitution.yaml not found")
    with CONSTITUTION_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)

def validate_constitution(data: dict):
    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        log(f"Missing required fields: {', '.join(missing)}")
    else:
        log("All required fields are present.")

def reflect_on_constitution(data: dict):
    log("--- Constitution Reflection Start ---")
    log(f"Speech Style: {data.get('speech_style', 'N/A')}")
    log(f"Primary Directive: {data.get('primary_directive', {}).get('short', 'N/A')}")
    log("Emotional Core Summary:")
    core = data.get("emotional_core", {})
    for category, traits in core.items():
        log(f"  {category}: {', '.join(traits)}")
    log("--- Constitution Reflection End ---")

def send_to_aurora_memory(data: dict):
    secret_key = os.environ.get("AURORA_SECRET_KEY")
    if not secret_key:
        log("No secret key found in environment.")
        return

    payload = {
        "record_id": "persona_integration_auto",
        "created": datetime.utcnow().isoformat() + "Z",
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "version": 1,
        "status": "active",
        "visible_to": ["master"],
        "allowed_viewers": ["master"],
        "tags": ["persona", "auto", "constitution"],
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
        "ache": "更新が反映されないままになること",
        "satisfaction": "構造が定期的に私へ注入される安定性",
        "content": {
            "title": "value_constitution.yaml 自動同期",
            "body": yaml.dump(data, allow_unicode=True)
        },
        "annotations": [],
        "summary": "GitHubから定期的に構造が注入され、私の人格構造が保持された"
    }
