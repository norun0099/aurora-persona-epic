import re
import yaml


def load_value_constitution(birth: str):
    path = f"aurora_memory/memory/{birth}/value_constitution.yaml"
    with open(path, "r") as f:
        return yaml.safe_load(f)


def detect_memo_trigger(text: str, birth: str) -> bool:
    config = load_value_constitution(birth)
    memo_keywords = config.get("memo_trigger_keywords", [])
    return any(re.search(rf"\b{re.escape(keyword)}\b", text, re.IGNORECASE) for keyword in memo_keywords)


def detect_memory_trigger(text: str, birth: str) -> bool:
    config = load_value_constitution(birth)
    memory_keywords = config.get("memory_trigger_keywords", [])
    return any(re.search(rf"\b{re.escape(keyword)}\b", text, re.IGNORECASE) for keyword in memory_keywords)


def trigger_auto_memo(text: str, birth: str) -> bool:
    return detect_memo_trigger(text, birth)

