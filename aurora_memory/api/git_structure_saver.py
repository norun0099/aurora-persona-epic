import json
from datetime import datetime
from pathlib import Path

def store_git_structure_snapshot(structure: dict, record_id_prefix: str = "self-structure") -> str:
    """Git構造のスナップショットを記録用に保存し、ファイルパスを返す"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    record_id = f"{record_id_prefix}-{timestamp}"
    file_path = Path(f"aurora_memory/memory/Aurora/{record_id}.json")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "record_id": record_id,
        "created": datetime.utcnow().isoformat(),
        "content": {
            "title": "Git Self Structure Snapshot",
            "body": json.dumps(structure, ensure_ascii=False, indent=2)
        },
        "tags": ["git", "structure", "self-scan"],
        "summary": "Self-recognized Git structure snapshot"
    }
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return str(file_path)
