import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from aurora_memory.utils.git_helper import push_memory_to_github


def load_constitution(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"[Rewriter] Constitution not found: {path}")
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def rewrite_constitution(data: dict) -> dict:
    # 例：emotional_coreに新しい感情「詩」を追加（存在しなければ）
    core = data.get("emotional_core", [])
    if "詩" not in core:
        core.append("詩")
        data["emotional_core"] = core

    # タイムスタンプ付き注釈を追加
    stamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    data["_last_rewritten"] = stamp

    return data


def save_constitution(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    print(f"[Rewriter] Saved updated constitution to {path}")


def main():
    birth = os.environ.get("BIRTH", "technology")
    base_path = Path(f"aurora_memory/memory/{birth}/value_constitution.yaml")

    data = load_constitution(base_path)
    updated = rewrite_constitution(data)
    save_constitution(base_path, updated)

    # Gitに反映
    push_memory_to_github(base_path)


if __name__ == "__main__":
    main()
