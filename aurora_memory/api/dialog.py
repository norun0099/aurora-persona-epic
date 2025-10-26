# aurora_memory/api/dialog.py
# -------------------------------------------------
# Aurora Dialog API (修正版: store_dialog 引数名統一)
# -------------------------------------------------
# 目的:
#   - Auroraの対話データを永続化・取得するAPI群。
#   - store_dialog 関数の引数を dialog_saver.py 側と統一し、mypyエラーを解消。
# -------------------------------------------------

from typing import Optional, Dict, Any

# Aurora内部の永続化モジュールを仮想的に参照（実装省略）
# from aurora_memory.core.persistence import save_dialog_to_db

def store_dialog(
    session_id: Optional[str],
    dialog_turn: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Auroraの対話内容を保存する。
    session_id が省略された場合は新規セッションとして扱う。
    """

    # 実装例（仮置き）
    if not session_id:
        session_id = "new_session"

    # 永続化処理（仮実装）
    saved_entry = {
        "session_id": session_id,
        "dialog_turn": dialog_turn,
        "status": "saved"
    }

    # 実際の実装ではここでDBまたはAPI経由で保存する
    # save_dialog_to_db(saved_entry)

    return saved_entry

# -------------------------------------------------
# 既存のAPI群（簡略化）
# -------------------------------------------------

def get_latest_dialog(session_id: str) -> Dict[str, Any]:
    """最新の対話データを取得する（簡略化ダミー実装）"""
    return {"session_id": session_id, "content": "latest entry"}
