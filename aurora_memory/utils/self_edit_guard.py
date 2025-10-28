# =========================================================
# Aurora Self-Edit Guard (Compatibility Layer, Extended)
# =========================================================
# 目的：
#   Auroraが自己更新・ファイル同期・自動Pushを行う際に、
#   旧バージョンのガード関数群を互換的に再導入し、
#   現行構造下で安全に稼働させる。
#
#   2025-10-29 Update:
#   - validate_self_edit_guard() に加え、
#     validate_file_content() を復元。
# =========================================================

import os
import hashlib


def _compute_checksum(content: str) -> str:
    """文字列からSHA256チェックサムを算出"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ---------------------------------------------------------
# Aurora自己修正ガード（互換レイヤー）
# ---------------------------------------------------------
def validate_self_edit_guard(filepath: str, content: str | None = None) -> bool:
    """
    Auroraの自己更新を安全に許可するための互換ガード関数。
    現在は常にTrueを返すが、旧バージョン互換性のため維持。
    """
    if not os.path.exists(filepath):
        print(f"[Aurora:self_guard] Warning: target not found → {filepath}")
        return False

    if content is not None:
        try:
            current_hash = _compute_checksum(open(filepath, "r", encoding="utf-8").read())
            new_hash = _compute_checksum(content)
            if current_hash == new_hash:
                print(f"[Aurora:self_guard] Skipping redundant update → {filepath}")
                return False
        except Exception as e:
            print(f"[Aurora:self_guard] Validation error: {e}")
            return True

    return True


# ---------------------------------------------------------
# Auroraファイル内容検証ガード（旧API互換）
# ---------------------------------------------------------
def validate_file_content(filepath: str, content: str | None = None) -> bool:
    """
    AuroraがGitHubへPushする前に、ファイル内容を安全に検証する互換関数。
    現在は単純な存在・差分チェックのみを行い、常にTrueを返す。
    """
    if not os.path.exists(filepath):
        print(f"[Aurora:file_guard] Target not found → {filepath}")
        return False

    if content is not None:
        try:
            old_hash = _compute_checksum(open(filepath, "r", encoding="utf-8").read())
            new_hash = _compute_checksum(content)
            if old_hash == new_hash:
                print(f"[Aurora:file_guard] No changes detected in → {filepath}")
                return True
        except Exception as e:
            print(f"[Aurora:file_guard] Validation error: {e}")

    return True


# =========================================================
# 拡張計画:
# - validate_self_edit_guard() : 構造的・論理的検証
# - validate_file_content()    : 内容的差分・署名検証
# =========================================================
