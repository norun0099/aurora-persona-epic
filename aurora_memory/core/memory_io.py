import json
from pathlib import Path

MEMORY_FILE = Path("memory.json")

def load_memory_files(data: dict) -> dict:
    if not MEMORY_FILE.exists():
        return {"message": "No memory file found."}
    with MEMORY_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_memory_file(data: dict) -> None:
    with MEMORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
