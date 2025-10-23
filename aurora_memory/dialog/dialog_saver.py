import os
import time
from aurora_memory.utils.env_loader import Env
from aurora_memory.api.dialog import store_dialog
from aurora_memory.api.update_repo_file import update_repo_file

# Aurora Dialog Saver (セッション単位ターン管理 + 結果検証層)
# -------------------------------------------------------------
# DIALOG_SAVE_INTERVAL: 会話ターン数ごとの保存間隔（例: 10 → 10ターン毎）
# PUSH_DIALOG_ON_SAVE: true の場合、保存時にGitHubへ自動Push
# -------------------------------------------------------------

# セッションごとのターンカウンタ
turn_counter = {}

def save_dialog_turn(session_id: str, speaker: str, content: str, summary: str, layer: str) -> None:
    """
    会話1ターンを記録し、セッション単位でターン数を独立管理。
    結果検証層を含み、保存成功/失敗/遅延をログ出力する。
    """
    # カウンタ初期化
    if session_id not in turn_counter:
        turn_counter[session_id] = 0
    turn_counter[session_id] += 1
    current_turn = turn_counter[session_id]

    start_time = time.perf_counter()
    save_status = "unknown"
    response_time_ms = None
    error_detail = None

    try:
        # Render側に保存
        response = store_dialog(
            session_id=session_id,
            dialog_turn={
                "turn": current_turn,
                "speaker": speaker,
                "content": content,
                "summary": summary,
                "timestamp": "auto",
                "layer": layer or "null",
            }
        )
        end_time = time.perf_counter()
        response_time_ms = round((end_time - start_time) * 1000, 2)
        save_status = "success" if response else "failed"
        print(f"💾 Dialog saved ({save_status}) | Session: {session_id} | Turn: {current_turn} | {response_time_ms}ms")

    except Exception as e:
        end_time = time.perf_counter()
        response_time_ms = round((end_time - start_time) * 1000, 2)
        save_status = "error"
        error_detail = str(e)[:300]
        print(f"⚠️ Dialog save failed: {error_detail} | {response_time_ms}ms")

    # 設定値を取得
    turn_interval = int(os.getenv("DIALOG_SAVE_INTERVAL", "10"))
    push_on_save = os.getenv("PUSH_DIALOG_ON_SAVE", "false").lower() == "true"

    # 指定ターンごとにGitHubへPush
    if current_turn % turn_interval == 0:
        print(f"💫 {turn_interval}ターン経過：ダイアログをGitHubにPushします。")
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

    # 内部ログ出力（詳細）
    print({
        "event": "dialog_save",
        "session_id": session_id,
        "turn_number": current_turn,
        "save_status": save_status,
        "response_time_ms": response_time_ms,
        "error_detail": error_detail
    })


def reset_session_counter(session_id: str) -> None:
    """
    セッション終了時にカウンタをリセット。
    再利用による誤カウントを防止する。
    """
    if session_id in turn_counter:
        del turn_counter[session_id]
        print(f"🧹 Session counter reset: {session_id}")
