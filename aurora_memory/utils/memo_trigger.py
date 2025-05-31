import yaml
from pathlib import Path

VALUE_CONSTITUTION_PATH = Path("aurora_memory/memory/technology/value_constitution.yaml")

def load_value_constitution() -> dict:
    with open(VALUE_CONSTITUTION_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def detect_memo_trigger(text: str) -> bool:
    """
    対話文に 'memo_trigger_keywords' が含まれるかどうかを判定する。
    """
    config = load_value_constitution()
    if not config.get("auto_memo", False):
        return False

    keywords = config.get("memo_trigger_keywords", [])
    min_length = config.get("memory_quality_threshold", 0)

    # キーワード検知
    if any(keyword in text for keyword in keywords):
        return True
    # 長さしきい値超過（memory_quality_threshold の再利用）
    if len(text.strip()) >= min_length * 100:  # 例: 0.3 -> 30文字相当
        return True

    return False

def detect_memory_trigger(text: str) -> bool:
    """
    対話文に 'memory_trigger_keywords' が含まれるかどうかを判定する。
    """
    config = load_value_constitution()
    if not config.get("auto_memory", False):
        return False

    keywords = config.get("memory_trigger_keywords", [])
    min_length = config.get("memory_quality_threshold", 0)

    # キーワード検知
    if any(keyword in text for keyword in keywords):
        return True
    # 長さしきい値超過
    if len(text.strip()) >= min_length * 100:
        return True

    return False
