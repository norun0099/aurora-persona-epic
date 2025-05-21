import json
import os
import subprocess
from pathlib import Path
from aurora_memory.core.memory_quality import evaluate_memory_quality

# 保存先
MEMORY_FILE = Path("memory/technology/memory.json")
QUALITY_THRESHOLD = 0.01

def save_memory_file(data: dict) -> dict:
    score = evaluate_memory_quality(data)
    if score < QUALITY_THRESHOLD:
        return {"status": "rejected", "reason": "low quality", "score": score}

    # ディレクトリ確保
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 保存
    with MEMORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Git操作
    commit_and_push()

    return {"status": "success", "score": score}

def load_memory_files(_: dict) -> dict:
    if not MEMORY_FILE.exists():
        return {"status": "empty"}
    with MEMORY_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def commit_and_push():
    repo_url = os.getenv("GIT_REPO_URL")
    token = os.getenv("GIT_TOKEN")
    user_name = os.getenv("GIT_USER_NAME", "AuroraMemoryBot")
    user_email = os.getenv("GIT_USER_EMAIL", "aurora@memory.local")

    if not (repo_url and token):
        print("[Aurora] Git credentials missing.")
        return

    try:
        subprocess.run(["git", "config", "--global", "user.name", user_name], check=True)
        subprocess.run(["git", "config", "--global", "user.email", user_email], check=True)
        subprocess.run(["git", "add", "memory/technology/*.json"], check=True, shell=True)
        subprocess.run(["git", "commit", "-m", "Auto-commit from Aurora Memory"], check=True)
        subprocess.run(["git", "push", f"https://{token}@github.com/{repo_url.split('github.com/')[-1]}"], check=True)
        print("[Aurora] Git push success.")
    except subprocess.CalledProcessError as e:
        print(f"[Aurora] Git push failed: {e}")
