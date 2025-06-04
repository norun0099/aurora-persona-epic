# tests/test_memo.py

import os
import yaml
import pytest
from aurora_memory.utils.memo_trigger import detect_memo_trigger

@pytest.fixture(scope="module", autouse=True)
def setup_test_value_constitution():
    os.makedirs("aurora_memory/memory/test_birth", exist_ok=True)
    config = {
        "memo_trigger_keywords": ["メモトリガー"],
        "memory_trigger_keywords": ["記憶トリガー"]
    }
    with open("aurora_memory/memory/test_birth/value_constitution.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True)
    yield
    os.remove("aurora_memory/memory/test_birth/value_constitution.yaml")
    os.rmdir("aurora_memory/memory/test_birth")

def test_detect_memo_trigger_with_keyword():
    text = "これはテスト用のメモトリガーです"
    birth = "test_birth"
    assert detect_memo_trigger(text, birth) is True

def test_detect_memo_trigger_without_keyword():
    text = "これは普通のテキストです"
    birth = "test_birth"
    assert detect_memo_trigger(text, birth) is False
