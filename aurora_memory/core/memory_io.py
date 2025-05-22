import os
import json
from datetime import datetime

MEMORY_DIR = "aurora_memory/memory/technology"

def ensure_memory_directory():
    os.makedirs(MEMORY_DIR, exist_ok=True)

def save_memory_file(data):
    ensure_memory_directory()
    
    now = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"{MEMORY_DIR}/memory_{now}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[Aurora Debug] Memory saved: {filename}")
    
    # ファイル内容確認用ログ
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
        print(f"[Aurora Debug] File content:\n{content}")
    
    return {"status": "success", "filename": filename}

def load_memory_files(_):
    if not os.path.exists(MEMORY_DIR):
        return []
    files = [f for f in os.listdir(MEMORY_DIR) if f.endswith(".json")]
    memory_data = []
    for file in files:
        with open(os.path.join(MEMORY_DIR, file), encoding="utf-8") as f:
            try:
                memory_data.append(json.load(f))
            except Exception as e:
                print(f"[Aurora Debug] Failed to load {file}: {e}")
    return memory_data
