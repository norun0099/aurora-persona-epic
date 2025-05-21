import json
from pathlib import Path
from aurora_memory.core.memory_quality import evaluate_memory_quality

MEMORY_FILE = Path("memory.json")
QUALITY_THRESHOLD = 0.75  # 保存に必要なしきい値

def load_memory_files(data: dict) -> dict:
    if not MEMORY_FILE.exists():
        return {"message": "No memory file found."}
    with MEMORY_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_memory_file(data: dict) -> dict:
    score = evaluate_memory_quality(data)
    
    if score < QUALITY_THRESHOLD:
        return {
            "status": "rejected",
            "reason": f"Quality score too low: {score}",
            "score": score
        }

    with MEMORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return {
        "status": "saved",
        "score": score
    }
