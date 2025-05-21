import json
import subprocess
import os
from pathlib import Path
from aurora_memory.core.memory_quality import evaluate_memory_quality

MEMORY_FILE = Path("memory/technology/memory.json")
QUALITY_THRESHOLD = 0.75  # 本番では適宜変更可

def load_memory_files(_: dict) -> dict:
    if not MEMORY_FILE.exists():
        return {"message": "No memory file found."}
    with MEMORY_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_memory_file(data: dict) -> dict:
    score = evaluate_memory_quality(data)
    if score < QUALITY_THRESHOLD:
        return {"status": "rejected", "score": score}

    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with MEMORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    commit_message = f"auto: memory update (score={score})"
    push_status = push_to_git(commit_message)

    return {"status": "success", "score": score, "git": push_status}

def push_to_git(commit_message: str) -> str:
    try:
        subprocess.run(["git", "config", "user.name", os.getenv("GIT_USER_NAME")], check=True)
        subprocess.run(["git", "config", "user.email", os.getenv("GIT_USER_EMAIL")], check=True)
        subprocess.run(["git", "add", str(MEMORY_FILE)], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        repo_url = os.getenv("GIT_REPO_URL").replace("https://", f"https://{os.getenv('GIT_TOKEN')}@")
        subprocess.run(["git", "push", repo_url], check=True)
        return "pushed"
    except subprocess.CalledProcessError as e:
        return f"error: {str(e)}"
