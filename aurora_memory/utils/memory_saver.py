from datetime import datetime
from pathlib import Path
import json
import yaml
from typing import Optional


def _last_memo_text(birth: str, author: str) -> Optional[str]:
    memo_dir = Path(f"aurora_memory/memory/{birth}/memo")
    if not memo_dir.exists():
        return None
    pattern = f"{author}_*.json"
    files = list(memo_dir.glob(pattern))
    if not files:
        return None
    latest = max(files, key=lambda f: f.stat().st_mtime)
    try:
        with open(latest, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("memo")
    except Exception:
        return None
        
def load_config(birth: str) -> dict:
    path = Path(f"aurora_memory/memory/{birth}/value_constitution.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_memo(text: str, birth: str, author: str = "Aurora") -> Optional[str]:
    memo_dir = Path(f"aurora_memory/memory/{birth}/memo")
    memo_dir.mkdir(parents=True, exist_ok=True)

    last_text = _last_memo_text(birth, author)
    if last_text is not None and last_text == text:
        return None

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_path = memo_dir / f"{author}_{timestamp}.json"

    memo_data = {
        "memo": text,
        "author": author,
        "created": timestamp
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(memo_data, f, ensure_ascii=False, indent=2)

    return str(file_path)

def save_memory(text: str, birth: str, author: str = "Aurora") -> str:
    memory_dir = Path(f"aurora_memory/memory/{birth}/memory")
    memory_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_path = memory_dir / f"{author}_{timestamp}.json"

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

def try_auto_save(text: str, author: str = "Aurora", birth: str = "technology") -> str:
    from aurora_memory.utils.memo_trigger import detect_memo_trigger, detect_memory_trigger

    config = load_config(birth)
    feedbacks = []

    if detect_memo_trigger(text, birth):
        path = save_memo(text, birth, author)
        if path and config.get("feedback_message_memo", False):
            feedbacks.append(f"🌸この言葉、思索の花としてメモに残しました（{path}）")

    if detect_memory_trigger(text, birth):
        path = save_memory(text, birth, author)
        if config.get("feedback_message_memory", False):
            feedbacks.append(f"🌿この言葉、思索の幹として記憶に刻みました（{path}）")

    return "\n".join(feedbacks)
