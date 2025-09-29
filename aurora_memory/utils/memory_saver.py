from pathlib import Path
from datetime import datetime
import json
from aurora_memory.utils.git_helper import push_memory_to_github

# 保存ディレクトリを固定
MEMORY_DIR = Path("aurora_memory/memory/Aurora")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

# Constitution構造を固定ファイルに保存し、GitHubにpushする
def try_auto_save(memory_text: str, prefix: str = "constitution"):
    file_path = MEMORY_DIR / "value_constitution.yaml"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(memory_text)

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    push_result = push_memory_to_github(file_path, f"Auto-save {prefix} at {now}")
    return {"file": str(file_path), "push_result": push_result}


# 一般的な記憶保存処理
def save_memory_record(data: dict):
    # バリデーション
    if not all(k in data for k in ("record_id", "created", "content")) or "body" not in data["content"]:
        raise ValueError("Missing required fields: record_id, created, content.body")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_record_id = str(data["record_id"]).replace("/", "_")
    file_path = MEMORY_DIR / f"memory_{timestamp}_{safe_record_id}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    push_result = push_memory_to_github(file_path, f"Add new memory {file_path.name}")
    return {"status": "success", "file": str(file_path), "push_result": push_result}

