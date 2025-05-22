import os
import json
from datetime import datetime
from pathlib import Path

MEMORY_ROOT = Path(__file__).resolve().parent.parent / "memory"
VALID_BIRTHS = {"technology", "primitive", "emotion", "logic", "narrative", "identity"}

def validate_memory_structure(data: dict) -> None:
    if not isinstance(data.get("visible_to"), list) or not data["visible_to"]:
        raise ValueError("visible_to must be a non-empty list.")
    for birth in data["visible_to"]:
        if birth not in VALID_BIRTHS:
            raise ValueError(f"visible_to contains invalid birth name: {birth}")
    
    if not isinstance(data.get("tags"), list) or not data["tags"]:
        raise ValueError("tags must be a non-empty list.")
    if data["tags"][0] not in VALID_BIRTHS:
        raise ValueError("The first tag must be a valid birth name.")

    if data.get("author") not in VALID_BIRTHS:
        raise ValueError("author must be one of the valid birth names.")

def save_memory_file(data: dict, category: str = "technology") -> str:
    validate_memory_structure(data)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    file_name = f"{timestamp}.json"
    dir_path = MEMORY_ROOT / category
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / file_name
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Aurora Debug] Memory saved to {file_path}")
    return str(file_path)

def load_memory_files(category: str = "technology") -> list:
    dir_path = MEMORY_ROOT / category
    if not dir_path.exists():
        return []
    files = sorted(dir_path.glob("*.json"))
    memories = []
    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                memories.append(json.load(f))
        except json.JSONDecodeError:
            print(f"[Aurora Warning] Failed to load {file}")
    return memories
