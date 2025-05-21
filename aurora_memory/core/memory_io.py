import json
from pathlib import Path
from aurora_memory.core.memory_quality import evaluate_memory_quality

# 絶対パスでルートから保存先を指定
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEMORY_FILE = BASE_DIR / "memory" / "technology" / "memory.json"

QUALITY_THRESHOLD = 0.01  # 一時的に保存スコアを緩和中

def load_memory_files(data: dict) -> dict:
    if not MEMORY_FILE.exists():
        return {"message": "No memory file found."}
    with MEMORY_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_memory_file(data: dict) -> dict:
    quality = evaluate_memory_quality(data)
    if quality < QUALITY_THRESHOLD:
        return {"status": "skipped", "quality": quality}

    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with MEMORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {"status": "success", "quality": quality}
