import yaml
from pathlib import Path
from datetime import datetime

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


def main():
    try:
        constitution = load_constitution()
        validate_constitution(constitution)
        reflect_on_constitution(constitution)
        log("Constitution validation and reflection complete.")
    except Exception as e:
        log(f"Error during validation: {e}")


if __name__ == "__main__":
    main()
