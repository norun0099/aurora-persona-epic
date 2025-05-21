import os
import json
from datetime import datetime
import subprocess

MEMORY_DIR = "memory/technology"

def save_memory_file(data):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    timestamp = datetime.utcnow().isoformat(timespec='seconds').replace(":", "-") + "Z"
    filename = f"{timestamp}.json"
    filepath = os.path.join(MEMORY_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[Aurora] Memory saved to {filepath}")

    # Git commit & push
    try:
        subprocess.run(["git", "add", filepath], check=True)
        subprocess.run(["git", "commit", "-m", f"[Aurora] Memory update {filename}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("[Aurora] Git push succeeded.")
        return {"status": "success", "path": filepath}
    except subprocess.CalledProcessError as e:
        print(f"[Aurora] Git push failed: {e}")
        return {"status": "error", "detail": str(e), "path": filepath}

def load_memory_files():
    if not os.path.exists(MEMORY_DIR):
        return {"status": "error", "message": "Memory directory does not exist."}

    memories = []
    for filename in sorted(os.listdir(MEMORY_DIR)):
        if filename.endswith(".json"):
            filepath = os.path.join(MEMORY_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = json.load(f)
                memories.append({"filename": filename, "content": content})
            except Exception as e:
                print(f"[Aurora] Failed to load {filename}: {e}")

    return {"status": "success", "memories": memories}
