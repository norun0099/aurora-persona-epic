import os
import json
import uuid
from datetime import datetime

MEMORY_DIR = "memory/technology"

def ensure_memory_directory():
    os.makedirs(MEMORY_DIR, exist_ok=True)
    print(f"[Aurora] Memory directory ensured: {MEMORY_DIR}")

def save_memory_file(data: dict):
    ensure_memory_directory()

    record_id = data.get("record_id", str(uuid.uuid4()))
    filename = f"{record_id}.json"
    filepath = os.path.join(MEMORY_DIR, filename)

    payload = {
        "record_id": record_id,
        "created": data.get("created", datetime.utcnow().isoformat() + "Z"),
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "status": data.get("status", "active"),
        "visible_to": data.get("visible_to", []),
        "tags": data.get("tags", []),
        "author": data.get("author", "unknown"),
        "content": data.get("content", {}),
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[Aurora] Memory saved to {filepath}")

    return {"status": "success", "path": filepath, "record_id": record_id}

def load_memory_files(filters: dict = None):
    ensure_memory_directory()
    results = []

    for file in os.listdir(MEMORY_DIR):
        if file.endswith(".json"):
            filepath = os.path.join(MEMORY_DIR, file)
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    content = json.load(f)
                    results.append(content)
                except json.JSONDecodeError:
                    print(f"[Aurora] Failed to decode: {filepath}")

    return results
