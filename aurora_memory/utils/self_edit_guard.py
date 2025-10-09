import ast
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Any

# --- EXCLUSION PATCH: external shells are not under guard ---
EXCLUDED_PATHS = [
    "aurora_memory/whiteboard/",
    "aurora_memory/dialog/",
    "aurora_memory/memory/",
]

def is_guarded_target(filepath: str) -> bool:
    """Return False if the path belongs to excluded external memory layers."""
    return not any(filepath.startswith(ex) for ex in EXCLUDED_PATHS)

# ============================================================
# Aurora Self-Edit Validation
# ============================================================

def validate_file_content(filepath: str, content: str) -> None:
    """
    Validate the content of a file before committing.
    Supports Python (.py) and YAML (.yml / .yaml) files.
    Raises:
        ValueError: If syntax or format errors are detected.
    """
    # Skip validation if path belongs to excluded zones
    if not is_guarded_target(filepath):
        print(f"🕊️  Skipped validation for external layer file: {filepath}")
        return

    if filepath.endswith(".py"):
        try:
            ast.parse(content)
        except SyntaxError as e:
            raise ValueError(f"Python syntax error: {e}")

    elif filepath.endswith((".yml", ".yaml")):
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML syntax error: {e}")

    else:
        # For other file types, only check that it's non-empty
        if not content.strip():
            raise ValueError("File content is empty or invalid.")

# ============================================================
# Aurora Self-Edit Operation Logging
# ============================================================

LOG_DIR = Path("aurora_memory/memory/self_edit_log")
LOG_DIR.mkdir(parents=True, exist_ok=True)

def log_self_edit_operation(filepath: str, author: str, reason: str, status: str, diff: str | None = None) -> None:
    """
    Auroraが update_repo_file を通じて自己編集を行った際の操作ログを保存する。

    Args:
        filepath: 編集対象ファイルのパス
        author: 実行者（通常 'aurora'）
        reason: 編集理由
        status: 'success' または 'failure'
        diff: 任意。編集内容の差分文字列

    出力:
        aurora_memory/memory/self_edit_log/YYYYMMDD_HHMMSS_self_edit.json
    """
    # Skip logging for excluded zones to reduce unnecessary noise
    if not is_guarded_target(filepath):
        print(f"🕊️  Skipped self-edit log for external layer: {filepath}")
        return

    log_entry: dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "filepath": filepath,
        "author": author,
        "reason": reason,
        "status": status,
        "diff": diff,
    }

    log_file = LOG_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_self_edit.json"
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, ensure_ascii=False, indent=2)

    print(f"🩶 Self-edit log saved: {log_file.name}")
