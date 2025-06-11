import os
import time
import yaml
import subprocess
from pathlib import Path
from datetime import datetime
from threading import Lock

LOCK_FILE = "/tmp/whiteboard_sync.lock"
LOG_FILE = "aurora_memory/utils/whiteboard.log"
WHITEBOARD_PATH_TEMPLATE = "aurora_memory/memory/{birth}/whiteboard.yaml"

GIT_USER_NAME = os.getenv("GIT_USER_NAME", "AuroraMemoryBot")
GIT_USER_EMAIL = os.getenv("GIT_USER_EMAIL", "aurora@memory.bot")
GIT_REPO_URL = os.getenv("GIT_REPO_URL")

lock = Lock()

def log(message: str):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def acquire_lock() -> bool:
    if os.path.exists(LOCK_FILE):
        log("Lock file exists. Aborting execution.")
        return False
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    return True

def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

def save_whiteboard(birth: str, content: dict) -> bool:
    path = Path(WHITEBOARD_PATH_TEMPLATE.format(birth=birth))
    path.parent.mkdir(parents=True, exist_ok=True)
    new_text = yaml.dump(content, allow_unicode=True, sort_keys=False)
    original = path.read_text(encoding="utf-8") if path.exists() else ""

    if new_text.strip() == original.strip():
        log("No changes in whiteboard. Skipping save.")
        return False

    with path.open("w", encoding="utf-8") as f:
        f.write(new_text)
    log(f"Saved whiteboard for birth '{birth}'")
    return True

def push_to_git(birth: str):
    try:
        subprocess.run(["git", "config", "user.name", GIT_USER_NAME], check=True)
        subprocess.run(["git", "config", "user.email", GIT_USER_EMAIL], check=True)
        subprocess.run(["git", "add", f"aurora_memory/memory/{birth}/whiteboard.yaml"], check=True)
        result = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if result.returncode != 0:
            subprocess.run(["git", "commit", "-m", f"Update whiteboard for {birth}"], check=True)
            subprocess.run(["git", "push"], check=True)
            log("Git push successful.")
        else:
            log("No changes to commit.")
    except subprocess.CalledProcessError as e:
        log(f"Git operation failed: {e}")

def sync_whiteboard(birth: str, notes: dict):
    if not acquire_lock():
        return

    try:
        changed = save_whiteboard(birth, notes)
        if changed:
            push_to_git(birth)
    finally:
        release_lock()

# Example usage:
# sync_whiteboard("emotion", {"author": "emotion", "notes": "Test note", "last_updated": "2025-06-11T10:00:00Z"})
