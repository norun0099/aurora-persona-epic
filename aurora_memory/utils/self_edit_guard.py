import json
from pathlib import Path
from typing import Any

def check_dialog_format_consistency(dialog_dir: Path) -> list[str]:
    """
    ダイアログJSONの構造を検査し、旧形式データを検出する。
    旧形式: 'turn', 'speaker', 'content' が直下に存在する。
    新形式: 'dialog_turn' キーを内包している。
    戻り値: 不一致を検出したファイル名リスト。
    """
    invalid_files = []

    for file in dialog_dir.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)

            if "dialog_turn" not in data and {"turn", "speaker", "content"} <= data.keys():
                invalid_files.append(file.name)
        except Exception as e:
            invalid_files.append(f"{file.name} (error: {e})")

    if invalid_files:
        print("⚠ 旧形式のダイアログファイルを検出しました：")
        for name in invalid_files:
            print(f" - {name}")
    else:
        print("✅ 全てのダイアログファイルは新形式（dialog_turn構造）です。")

    return invalid_files