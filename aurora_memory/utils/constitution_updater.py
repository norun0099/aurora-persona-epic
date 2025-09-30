import os
import yaml
from datetime import datetime
from git import Repo

CONSTITUTION_PATH = os.path.join(os.getcwd(), "aurora_memory/memory/Aurora/value_constitution.yaml")
REPO_PATH = os.getcwd()

def load_constitution() -> None:
    with open(CONSTITUTION_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def update_constitution(fields_to_update: dict) -> None:
    constitution = load_constitution()
    now_str = datetime.utcnow().isoformat()

    # versionとupdated_atを自動更新
    version = constitution.get("version", 0)
    constitution["version"] = version + 1
    constitution["updated_at"] = now_str

    # 指定フィールドを上書き
    for key, value in fields_to_update.items():
        constitution[key] = value

    # 保存
    with open(CONSTITUTION_PATH, 'w', encoding='utf-8') as f:
        yaml.safe_dump(constitution, f, allow_unicode=True)

    return constitution

def commit_and_push(reason: str, author: str = "aurora-self") -> None:
    repo = Repo(REPO_PATH)
    repo.git.add(CONSTITUTION_PATH)
    repo.index.commit(f"[auto] constitution update: {reason} ({author})")
    origin = repo.remote(name='origin')
    origin.push()

    return True
