import yaml
import os
import re

VALUE_CONSTITUTION_PATH = "aurora_memory/memory_protocol/value_constitution.yaml"

def load_value_constitution():
    with open(VALUE_CONSTITUTION_PATH, "r") as f:
        return yaml.safe_load(f)

def detect_memo_trigger(text: str) -> bool:
    config = load_value_constitution()
    memo_keywords = config.get("memo_trigger_keywords", [])
    return any(re.search(rf"\\b{re.escape(keyword)}\\b", text, re.IGNORECASE) for keyword in memo_keywords)

def detect_memory_trigger(text: str) -> bool:
    config = load_value_constitution()
    memory_keywords = config.get("memory_trigger_keywords", [])
    return any(re.search(rf"\\b{re.escape(keyword)}\\b", text, re.IGNORECASE) for keyword in memory_keywords)

def trigger_auto_memo(text: str) -> bool:
    return detect_memo_trigger(text)
