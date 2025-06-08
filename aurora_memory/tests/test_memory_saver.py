import os
import shutil
import yaml
from pathlib import Path
from aurora_memory.utils.memory_saver import try_auto_save


def setup_module(module):
    birth_dir = Path("aurora_memory/memory/test_auto")
    birth_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "memo_trigger_keywords": ["memo"],
        "memory_trigger_keywords": ["memory"],
        "feedback_message_memo": True,
        "feedback_message_memory": True,
    }
    with open(birth_dir / "value_constitution.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True)


def teardown_module(module):
    shutil.rmtree(Path("aurora_memory/memory/test_auto"))


def test_try_auto_save_creates_files():
    birth = "test_auto"
    feedback = try_auto_save("memo and memory", author="Tester", birth=birth)
    assert "思索の花としてメモに残しました" in feedback
    assert "思索の幹として記憶に刻みました" in feedback

    memo_dir = Path(f"aurora_memory/memory/{birth}/memo")
    memory_dir = Path(f"aurora_memory/memory/{birth}/memory")
    assert any(memo_dir.glob("Tester_*.json"))
    assert any(memory_dir.glob("Tester_*.json"))


def test_try_auto_save_skips_duplicate_memo():
    birth = "test_dup_auto"
    birth_dir = Path(f"aurora_memory/memory/{birth}")
    birth_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "memo_trigger_keywords": ["memo"],
        "memory_trigger_keywords": ["memory"],
        "feedback_message_memo": True,
        "feedback_message_memory": True,
    }
    with open(birth_dir / "value_constitution.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True)

    feedback1 = try_auto_save("memo and memory", author="Tester", birth=birth)
    feedback2 = try_auto_save("memo and memory", author="Tester", birth=birth)

    memo_dir = birth_dir / "memo"
    assert len(list(memo_dir.glob("Tester_*.json"))) == 1
    assert "思索の花としてメモに残しました" in feedback1
    assert "思索の花としてメモに残しました" not in feedback2

    shutil.rmtree(birth_dir)
