from typing import Any
import os
import yaml
from datetime import datetime
from git import Repo  # type: ignore[attr-defined]  ← GitPythonの型定義回避

CONSTITUTION_PATH = os.path.join(os.getcwd(), "aurora_memory/memory/Aurora/value_constitution.yaml")
REPO_PATH = os.getcwd()


def load_constitution() -> dict[str, Any]:
    """YAMLから現在の構造を読み込む"""
    with open(CONSTITUTION_PATH, "r", encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f) or {}
        return data


def update_constitution(fields_to_update: dict[str, Any]) -> dict[str, Any]:
    """構造データを更新し、versionと更新時刻を自動更新する"""
    constitution = load_constitution()
    now_str = datetime.utcnow().isoformat()

    version = constitution.get("version", 0)
    constitution["version"] = version + 1
    constitution["updated_at"] = now_str

    for key, value in fields_to_update.items():
        constitution[key] = value

    with open(CONSTITUTION_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(constitution, f, allow_unicode=True)

    return constitution


def commit_and_push(reason: str, author: str = "aurora-self") -> None:
    """更新内容をGitにコミット・プッシュする"""
    repo = Repo(REPO_PATH)
    repo.git.add(CONSTITUTION_PATH)
    repo.index.commit(f"[auto] constitution update: {reason} ({author})")
    origin = repo.remote(name="origin")
    origin.push()
