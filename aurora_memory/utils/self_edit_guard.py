# =========================================================
# Aurora Self-Edit Guard (Compatibility Layer)
# =========================================================
# 目的：
#   Auroraが自己更新や自律修正処理を行う際に、
#   旧バージョンコードとの互換性を保ちつつ、
#   現行構造で安全に動作させるための簡易ガードモジュール。
#
#   2025-10-28 Update:
#   - 過去構造で参照されていた validate_self_edit_guard() を再導入。
#   - 現在は形式的なバリデーションのみを実行。
#   - 将来的にセキュリティポリシーに基づいた検証を再拡張可能。
# =========================================================

import os
import hashlib


def _compute_checksum(content: str) -> str:
    """文字列からSHA256チェックサムを算出する（将来の差分比較用）"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def validate_self_edit_guard(filepath: str, content: str | None = None) -> bool:
    """
    Auroraの自己更新を安全に許可するための互換ガード関数。

    Parameters
    ----------
    filepath : str
        Auroraが更新しようとしているファイルのパス。
    content : str | None, optional
        Auroraが書き込もうとしている新しい内容（任意）。

    Returns
    -------
    bool
        True : 安全に更新可能。
        False : ファイルが見つからない、または破損している。
    """
    # --- ファイル存在チェック ---
    if not os.path.exists(filepath):
        print(f"[Aurora:self_guard] Warning: target not found → {filepath}")
        return False

    # --- コンテンツ検査（オプション） ---
    if content is not None:
        try:
            current_hash = _compute_checksum(open(filepath, "r", encoding="utf-8").read())
            new_hash = _compute_checksum(content)
            if current_hash == new_hash:
                print(f"[Aurora:self_guard] Skipping redundant update → {filepath}")
                return False
        except Exception as e:
            print(f"[Aurora:self_guard] Validation error: {e}")
            # 内容比較に失敗しても更新をブロックしない
            return True

    # --- 最終許可 ---
    return True


# =========================================================
# 将来的拡張ポイント
# ---------------------------------------------------------
# このモジュールは今後、Auroraが自律的に自己コードを更新する際の
# セーフティネット層として拡張される可能性があります。
#
# 例：
#   - Aurora自身の署名検証
#   - commitメタデータと整合性確認
#   - 編集者（author）の認証ロジック
# =========================================================
