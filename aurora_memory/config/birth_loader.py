import yaml
import os
from pathlib import Path

DEFAULT_BIRTHS = [
    "technology", "emotion", "desire",
    "primitive", "veil", "salon", "music", "request", "relation"
]

CONFIG_PATH = Path(__file__).parent / "global_births.yaml"

def load_births_from_yaml() -> list[str]:
    """
    Load the list of valid births from global_births.yaml.
    Falls back to DEFAULT_BIRTHS if the file is missing or invalid.
    """
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            births = data.get("births", [])
            if not isinstance(births, list) or not all(isinstance(b, str) for b in births):
                raise ValueError("Invalid format for births.")
            return births
    except Exception as e:
        print(f"[birth_loader] Warning: Failed to load births from YAML. Using default. Reason: {e}")
        return DEFAULT_BIRTHS
