import json
from pathlib import Path
from aurora_memory.core.memory_quality import evaluate_memory_quality

# Technology人格専用の保存先ディレクトリ
MEMORY_FILE = Path("aurora_memory/memory/technology/memory.json")
QUALITY_THRESHOLD = 0.01  # 一時的に保存許可スコアを緩和

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

    # 保存先ディレクトリがなければ作成
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with MEMORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {
        "status": "saved",
        "score": score,
        "path": str(MEMORY_FILE)
    }
