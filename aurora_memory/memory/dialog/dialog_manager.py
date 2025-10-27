from typing import Any, Optional, cast

# ...（既存のインポートや関数定義部分）...

# 行93付近の修正版

def handle_dialog_data() -> None:
    """最新のダイアログデータを安全に取得し処理する。"""
    try:
        from aurora_memory.dialog.dialog_reflector import get_latest_dialog
        dialog_data: Optional[dict[str, Any]] = get_latest_dialog()

        # None対策：mypy整合性 + 実行時安定性
        if dialog_data is None:
            dialog_data = {}

        # 以下は既存の処理を安全に継続
        process_dialog_data(dialog_data)

    except Exception as e:
        print(f"⚠️ [DialogManager] Error handling dialog data: {e}")


def process_dialog_data(dialog_data: dict[str, Any]) -> None:
    """ダイアログデータの処理を行う（既存処理を安全化）"""
    # 既存のロジックをここに保持
    pass  # ← 実際のロジックがここに入る想定