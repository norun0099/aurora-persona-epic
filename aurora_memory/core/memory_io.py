import json
import subprocess
from pathlib import Path
from datetime import datetime

MEMORY_DIR = Path("memory/technology")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

def get_timestamp():
    return datetime.utcnow().strftime("%Y%m%dT%H%M%S")

def save_memory_file(data: dict) -> None:
    timestamp = get_timestamp()
    file_path = MEMORY_DIR / f"memory_{timestamp}.json"

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[Aurora] Memory saved to: {file_path}")

    try:
        subprocess.run(["git", "add", str(file_path)], check=True)
        print("[Aurora] Git add successful.")

        commit_message = f"[Aurora] Auto memory commit at {timestamp}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print("[Aurora] Git commit successful.")

        subprocess.run(["git", "push"], check=True)
        print("[Aurora] Git push successful.")
    except subprocess.CalledProcessError as e:
        print(f"[Aurora] Git push failed: {e}")
