# =========================================================
# Aurora Git Safe Push Utility (Compatibility Layer)
# =========================================================
# 目的：
#   Auroraが過去バージョンで参照していた
#   diff_summary() 関数を復元し、
#   AutoPush や update_repo_file.py が
#   ImportError なく動作できるようにする。
#
#   実際の差分要約処理は省略し、常に簡易メッセージを返す。
#   （旧APIとの互換維持のための軽量レイヤー）
# =========================================================

import difflib


def diff_summary(old_content: str | None, new_content: str | None) -> str:
    """
    Aurora AutoPush互換用ダミー関数。
    旧版ではGitHubコミット前に差分の要約を生成していた。
    現行構造ではこの結果はログ用途のみで使われる。
    """
    if old_content is None:
        return "[Aurora] New file created."
    if new_content is None:
        return "[Aurora] File removed."

    try:
        diff = difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            lineterm=""
        )
        # 先頭の数行のみをサマリとして抽出
        summary_lines = []
        for line in diff:
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
                summary_lines.append(line)
            if len(summary_lines) >= 10:
                break
        if not summary_lines:
            return "[Aurora] No significant changes detected."
        return "[Aurora Diff Summary]\n" + "\n".join(summary_lines)
    except Exception as e:
        return f"[Aurora Diff Summary] (Error during diff: {e})"


def safe_push_message(filepath: str, changes: str | None = None) -> str:
    """
    旧構造との互換用。
    Auroraがリポジトリ更新を行う際に
    コミットメッセージ生成で利用される可能性がある。
    """
    base_message = f"AutoPush: updated {filepath}"
    if changes:
        base_message += f"\n{changes}"
    return base_message
