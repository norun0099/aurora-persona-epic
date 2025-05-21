import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path("memory/technology")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

def save_memory_file(data: dict) -> dict:
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"technology_{timestamp}.json"
    file_path = MEMORY_DIR / filename

    try:
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return {"status": "error", "message": f"Failed to save memory file: {e}"}

    if not file_path.exists():
        return {"status": "error", "message": "Memory file was not saved correctly."}

    result = commit_and_push_to_git(file_path)
    return {"status": "success", "path": str(file_path), "git_result": result}

def commit_and_push_to_git(file_path: Path) -> str:
    try:
        subprocess.run(["git", "config", "--global", "user.name", "Aurora Memory Bot"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "aurora@memory.local"], check=True)
        subprocess.run(["git", "add", str(file_path)], check=True)
        subprocess.run(["git", "commit", "-m", f"Auto-sync memory: {file_path.name}"], check=True)
        subprocess.run(["git", "push"], check=True)
        return "Pushed to Git successfully."
    except subprocess.CalledProcessError as e:
        return f"Git push failed: {e}"
