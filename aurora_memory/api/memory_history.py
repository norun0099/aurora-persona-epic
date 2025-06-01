from fastapi import APIRouter, Query
from pathlib import Path
import json
from typing import List, Dict, Any

router = APIRouter()

MEMORY_DIR = Path("aurora_memory/memory/technology")  # 例としてTechnologyバース

@router.get("/memory/history")
def get_memory_history(birth: str, limit: int = None) -> List[Dict[str, Any]]:
    """
    指定バースの記憶履歴を取得するAPI。
    最新順にソートし、limitがあれば上限をかける。
    """
    target_dir = Path(f"aurora_memory/memory/{birth}")
    if not target_dir.exists():
        return []

    memory_files = sorted(target_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    
    history = []
    for file in memory_files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            history.append(data)
            if limit and len(history) >= limit:
                break

    return history
