import os
import json
from datetime import datetime

MEMORY_DIRECTORY = "memory/technology"

def ensure_memory_directory():
    os.makedirs(MEMORY_DIRECTORY, exist_ok=True)

def generate_filename(title):
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    safe_title = "".join(c if c.isalnum() else "_" for c in title)[:50]
    return f"{safe_title}_{timestamp}.json"

def save_memory_file(data):
    ensure_memory_directory()
    filename = generate_filename(data.get("content", {}).get("title", "memory"))
    filepath = os.path.join(MEMORY_DIRECTORY, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return {"status": "success", "path": filepath, "score": 0.0294}

def load_memory_files(filters=None):
    ensure_memory_directory()
    memory_files = []
    for file in Path(MEMORY_DIRECTORY).glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            try:
                memory_data = json.load(f)
                memory_files.append(memory_data)
            except json.JSONDecodeError:
                continue
    return {"status": "success", "memories": memory_files}
