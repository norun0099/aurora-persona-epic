import re
import os
from pathlib import Path

BASE_DIR = Path("aurora_memory")

def process_file(path: Path):
    text = path.read_text(encoding="utf-8")
    original = text

    # 1. 関数定義に -> None を補完（既にある場合�E無視！E
    text = re.sub(
        r"^(\s*def\s+\w+\(.*\))\s*:$",
        r"\1 -> None:",
        text,
        flags=re.MULTILINE,
    )

    # 2. Dict めEdict[str, Any] に置揁E
    text = re.sub(r"\bDict\b", "dict[str, Any]", text)

    # 3. int = None ↁEOptional[int] = None
    text = re.sub(r":\s*int\s*=\s*None", ": Optional[int] = None", text)

    # 4. apscheduler の import に # type: ignore
    text = re.sub(r"^(from\s+apscheduler[^\n]+)$", r"\1  # type: ignore", text, flags=re.MULTILINE)

    # 5. typing のインポ�Eトを追加
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
