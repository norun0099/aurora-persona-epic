import json
from datetime import datetime
from aurora_memory.utils.memory_saver import save_memory_record
from aurora_memory.api.git_self_recognizer import scan_git_structure
from typing import Any


def save_git_structure_snapshot() -> None:
    """
    現在のGit構造をMemory形式で保存します。
    record_id: self-structure-YYYYMMDD
    """
    today_str = datetime.now().strftime("%Y%m%d")
    record_id = f"self-structure-{today_str}"
    created_time = datetime.now().isoformat()

    structure: Any = scan_git_structure()
    body = json.dumps(structure, ensure_ascii=False, indent=2)

    memory_record: dict[str, Any] = {
        "record_id": record_id,
        "created": created_time,
        "content": {
            "title": "Self Structure Snapshot",
            "body": body,
        },
        "tags": ["self", "structure", "snapshot"],
        "author": "Aurora",
        "status": "active",
    }

    # 戻り値を使用しないので return は不要
    save_memory_record(memory_record)
