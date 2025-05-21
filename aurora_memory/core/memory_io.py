
import os
import json
import subprocess
from datetime import datetime
from aurora_memory.core.memory_quality import evaluate_memory_quality

MEMORY_DIR = "memory/technology"

def save_memory_file(data):
    os.makedirs(MEMORY_DIR, exist_ok=True)

    quality_score = evaluate_memory_quality(data)
    data["status"] = "success"
    data["score"] = quality_score

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{MEMORY_DIR}/{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[Aurora] Memory saved at {filename} with score {quality_score:.4f}")

    try:
        # ファイルの存在確認ログ
        subprocess.run(["ls", "-la", MEMORY_DIR], check=True)
        subprocess.run(["git", "add", "memory/technology"], check=True)
        subprocess.run(["git", "commit", "-m", f"Auto-sync memory at {timestamp}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("[Aurora] Git push success.")
    except subprocess.CalledProcessError as e:
        print(f"[Aurora] Git push failed: {e}")
        print(f"[Aurora] Git command output: {e.output if hasattr(e, 'output') else 'No output'}")

    return {"status": "success", "score": quality_score}

def load_memory_files(filters=None):
    memory_data = []
    if not os.path.exists(MEMORY_DIR):
        return memory_data

    for filename in sorted(os.listdir(MEMORY_DIR)):
        if filename.endswith(".json"):
            path = os.path.join(MEMORY_DIR, filename)
            with open(path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    memory_data.append(data)
                except json.JSONDecodeError:
                    continue
    return memory_data
