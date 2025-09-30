from pathlib import Path
from datetime import datetime
import json
from aurora_memory.utils.git_helper import push_memory_to_github

# 菫晏ｭ倥ョ繧｣繝ｬ繧ｯ繝医Μ繧貞崋螳・
MEMORY_DIR = Path("aurora_memory/memory/Aurora")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

# Constitution讒矩繧貞崋螳壹ヵ繧｡繧､繝ｫ縺ｫ菫晏ｭ倥＠縲；itHub縺ｫpush縺吶ｋ
def try_auto_save(memory_text: str, prefix: str = "constitution") -> None:
    file_path = MEMORY_DIR / "value_constitution.yaml"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(memory_text)

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    push_result = push_memory_to_github(file_path, f"Auto-save {prefix} at {now}")
    return {"file": str(file_path), "push_result": push_result}


# 荳闊ｬ逧・↑險俶・菫晏ｭ伜・逅・
def save_memory_record(data: dict) -> None:
    # 繝舌Μ繝・・繧ｷ繝ｧ繝ｳ
    if not all(k in data for k in ("record_id", "created", "content")) or "body" not in data["content"]:
        raise ValueError("Missing required fields: record_id, created, content.body")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_record_id = str(data["record_id"]).replace("/", "_")
    file_path = MEMORY_DIR / f"memory_{timestamp}_{safe_record_id}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    push_result = push_memory_to_github(file_path, f"Add new memory {file_path.name}")
    return {"status": "success", "file": str(file_path), "push_result": push_result}

