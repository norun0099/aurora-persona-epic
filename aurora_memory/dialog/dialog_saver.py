import os
from aurora_memory.utils.env_loader import Env
from aurora_memory.api.dialog import store_dialog
from aurora_memory.api.update_repo_file import update_repo_file

# Aurora Dialog Saver (会話記録の間隔制御版)
# -------------------------------------------------------------
# DIALOG_SAVE_INTERVAL: 会話ターン数ごとの保存間隔（例: 10 → 10ターン毎）
# PUSH_DIALOG_ON_SAVE: true の場合、保存時にGitHubへ自動Push
# -------------------------------------------------------------

turn_count = 0  # 会話ターンカウンタ

def save_dialog_turn(session_id: str, speaker: str, content: str, summary: str, layer: str) -> None:
    """会話1ターンを記録し、指定ターンごとに自動Pushを行う"""
    global turn_count
    turn_count += 1

    # Render側に保存
    store_dialog(
        session_id=session_id,
        dialog_turn={
            "turn": turn_count,
            "speaker": speaker,
            "content": content,
            "summary": summary,
            "timestamp": "auto",
            "layer": layer or "null",
        }
    )

    # 設定値を取得
    turn_interval = int(os.getenv("DIALOG_SAVE_INTERVAL", "10"))
    push_on_save = os.getenv("PUSH_DIALOG_ON_SAVE", "false").lower() == "true"

    # 指定ターンごとにGitHubへPush
    if turn_count % turn_interval == 0:
        print(f"💾 {turn_interval}ターン経過：ダイアログをGitHubにPushします。")
        if push_on_save:
            try:
                update_repo_file(
                    filepath=f"aurora_memory/dialog/{session_id}.json",
                    content="auto-sync-dialog",
                    author="AuroraMemoryBot",
                    reason="自動記録：会話インターバル到達によるPush",
                )
                print("🌸 ダイアログが正常にPushされました。")
            except Exception as e:
                print(f"⚠️ Push失敗: {e}")
        else:
            print("🕊️ PUSH_DIALOG_ON_SAVE=false のため、Pushはスキップされました。")
