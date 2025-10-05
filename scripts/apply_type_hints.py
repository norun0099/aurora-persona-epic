import re
from pathlib import Path

BASE_DIR = Path("aurora_memory")


def process_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    original = text

    # 1. FastAPI エンドポイント関数に dict[str, Any] を補完
    def repl_func(m: re.Match[str]) -> str:
        header = m.group(1)
        # FastAPI エンドポイント（@appや@router直後の関数）には dict[str, Any]
        if re.search(r"@(app|router)\.(get|post|put|delete|patch)", text[max(0, m.start()-100):m.start()]):
            return f"{header} -> dict[str, Any]:"
        # dictを返す関数
        if re.search(r"\\breturn\\b.+\\bdict\\b", text[m.start():m.end()]):
            return f"{header} -> dict[str, Any]:"
        # listを返す関数
        if re.search(r"\\breturn\\b.+\\blist\\b", text[m.start():m.end()]):
            return f"{header} -> list[Any]:"
        # デフォルトは None
        return f"{header} -> None:"

    text = re.sub(
        r"^(\s*def\s+\w+\(.*\))\s*:(?!\s*# type: ignore)",
        repl_func,
        text,
        flags=re.MULTILINE,
    )

    # 2. 引数の dict を dict[str, Any] に変換
    text = re.sub(r":\s*dict\\b", ": dict[str, Any]", text)

    # 3. Dict を dict[str, Any] に置換
    text = re.sub(r"\\bDict\\b", "dict[str, Any]", text)

    # 4. int = None → Optional[int] = None
    text = re.sub(r":\s*int\s*=\s*None", ": Optional[int] = None", text)

    # 5. str = None → Optional[str] = None
    text = re.sub(r":\s*str\s*=\s*None", ": Optional[str] = None", text)

    # 6. apscheduler の import に # type: ignore
    text = re.sub(
        r"^(from\s+apscheduler[^\n]+)$",
        r"\1  # type: ignore",
        text,
        flags=re.MULTILINE,
    )

    # 7. typing のインポートを追加
    if any(x in text for x in ["Any", "Optional", "Union"]):
        if "from typing import" not in text:
            text = "from typing import Any, Optional, Union\n" + text

    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"Updated {path}")


def main() -> None:
    for py_file in BASE_DIR.rglob("*.py"):
        process_file(py_file)


if __name__ == "__main__":
    main()