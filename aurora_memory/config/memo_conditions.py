from pathlib import Path
import yaml

CONDITION_FILE = Path("aurora_memory/config/memo_conditions.yaml")

def load_conditions():
    with open(CONDITION_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def check_conditions(memo_text: str, conditions: dict) -> bool:
    """
    条件（キーワード, 最小長, タグ, etc）をもとに、メモを保存対象とするかを判定
    """
    if "keywords" in conditions:
        for kw in conditions["keywords"]:
            if kw in memo_text:
                return True

    if "min_length" in conditions:
        if len(memo_text) >= conditions["min_length"]:
            return True

    # 追加の条件（例：タグや構造評価）をここに加えることも可

    return False
