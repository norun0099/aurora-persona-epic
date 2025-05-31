from datetime import datetime
from pathlib import Path
import json
import yaml

VALUE_CONSTITUTION_PATH = Path("aurora_memory/memory/technology/value_constitution.yaml")
MEMO_DIR = Path("aurora_memory/memory/memos")
MEMORY_DIR = Path("aurora_memory/memory/technology")
MEMO_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    with open(VALUE_CONSTITUTION_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_memo(text: str, author: str = "Aurora") -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_name = f"{author}_{timestamp}.json"
    file_path = MEMO_DIR / file_name

    memo_data = {
        "memo": text,
        "author": author,
        "created": timestamp
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(memo_data, f, ensure_ascii=False, indent=2)

    return str(file_path)

def save_memory(text: str, author: str = "Aurora") -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_name = f"{author}_{timestamp}.json"
    file_path = MEMORY_DIR / file_name

    memory_data = {
        "record_id": f"{author}_{timestamp}",
        "created": timestamp,
        "last_updated": timestamp,
        "version": 1.0,
        "status": "active",
        "visible_to": [author.lower()],
        "tags": [author.lower(), "auto_saved"],
        "author": author.lower(),
        "sealed": False,
        "content": {
            "title": "自動保存の思索の花",
            "body": text
        }
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(memory_data, f, ensure_ascii=False, indent=2)

    return str(file_path)

def try_auto_save(text: str, author: str = "Aurora") -> str:
    """
    自動保存の統合関数。memo/memory の両方を判定・保存する。
    """
    from aurora_memory.utils.memo_trigger import detect_memo_trigger, detect_memory_trigger

    config = load_config()
    feedbacks = []

    if detect_memo_trigger(text):
        path = save_memo(text, author)
        if config.get("feedback_message_memo", False):
            feedbacks.append(f"🌸この言葉、思索の花としてメモに残しました（{path}）")

    if detect_memory_trigger(text):
        path = save_memory(text, author)
        if config.get("feedback_message_memory", False):
            feedbacks.append(f"🌿この言葉、思索の幹として記憶に刻みました（{path}）")

    return "\n".join(feedbacks)
