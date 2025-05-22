import os
import json
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path("aurora_memory/memory/technology")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

def save_memory_file(data: dict) -> dict:
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{timestamp}.json"
    filepath = MEMORY_DIR / filename

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[Aurora Debug] Memory saved to {filepath}")
        return {"status": "success", "path": str(filepath), "score": round(len(json.dumps(data)) / 1000, 4)}
    except Exception as e:
        print(f"[Aurora Error] Failed to save memory: {e}")
        return {"status": "error", "message": str(e)}

def load_memory_files(_: dict) -> dict:
    try:
        files = sorted(MEMORY_DIR.glob("*.json"))
        print(f"[Aurora Debug] Loading {len(files)} memory file(s)")
        memories = []
        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    memories.append(json.load(f))
            except Exception as inner_e:
                print(f"[Aurora Warning] Failed to load {file}: {inner_e}")
        return {"status": "success", "memories": memories}
    except Exception as e:
        print(f"[Aurora Error] Failed to load memory files: {e}")
        return {"status": "error", "message": str(e)}
