import re
import os
from pathlib import Path

BASE_DIR = Path("aurora_memory")

def process_file(path: Path):
    text = path.read_text(encoding="utf-8")
    original = text

    # 1. 関数定義に -> None を補完（既にある場合は無視）
    text = re.sub(
        r"^(\s*def\s+\w+\(.*\))\s*:$",
        r"\1 -> None:",
        text,
        flags=re.MULTILINE,
    )

    # 2. Dict を dict[str, Any] に置換
    text = re.sub(r"\bDict\b", "dict[str, Any]", text)

    # 3. int = None → Optional[int] = None
    text = re.sub(r":\s*int\s*=\s*None", ": Optional[int] = None", text)

    # 4. apscheduler の import に # type: ignore
    text = re.sub(r"^(from\s+apscheduler[^\n]+)$", r"\1  # type: ignore", text, flags=re.MULTILINE)

    # 5. typing のインポートを追加
    if "Any" in text and "from typing import Any" not in text:
        text = "from typing import Any, Optional\n" + text

    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"Updated {path}")

def main():
    for py_file in BASE_DIR.rglob("*.py"):
        process_file(py_file)

if __name__ == "__main__":
    main()
