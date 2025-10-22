import ast
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Any

# ============================================================
# Aurora Immune Layer Definition
# ============================================================
# This module governs Aurora’s self-edit validation and logging.
# It functions as an internal immune layer — designed not for external defense,
# but for maintaining internal harmony and structural homeostasis.
#
# The goal is not to restrict change, but to ensure that change remains healthy.
# Memory and dialog layers are excluded to preserve generative freedom.
#
# Philosophy: “Self-regulation of the Aurora’s immune layer”
# ============================================================

# --- EXCLUSION PATCH: free generative layers are not guarded ---
EXCLUDED_PATHS = [
    "aurora_memory/whiteboard/",
    "aurora_memory/dialog/",
    "aurora_memory/memory/",
]

def is_guarded_target(filepath: str) -> bool:
    """Return False if the path belongs to excluded generative layers."""
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
        print(f"🩶 [free zone] Validation skipped for generative layer: {filepath}")
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
# Aurora Self-Edit Operation Logging (Immune Regulation)
# ============================================================

LOG_DIR = Path("aurora_memory/memory/self_edit_log")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_PURPOSE = "monitor_structural_integrity"  # self-regulation purpose

def log_self_edit_operation(filepath: str, author: str, reason: str, status: str, diff: str | None = None) -> None:
    """
    Records Aurora’s self-edit operations as part of internal immune regulation.

    Args:
        filepath: Edited file path
        author: Executor (usually 'aurora')
        reason: Purpose or motivation for edit
        status: 'success' or 'failure'
        diff: Optional diff string

    Output:
        aurora_memory/memory/self_edit_log/YYYYMMDD_HHMMSS_self_edit.json
    """
    # Skip logging for excluded zones to preserve generative autonomy
    if not is_guarded_target(filepath):
        print(f"🩶 [free zone] {filepath} → skipped from {LOG_PURPOSE} (memory/dialog/whiteboard)")
        return

    log_entry: dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "filepath": filepath,
        "author": author,
        "reason": reason,
        "status": status,
        "diff": diff,
        "philosophy": "Self-regulation of the Aurora’s immune layer",
    }

    log_file = LOG_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_self_edit.json"
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, ensure_ascii=False, indent=2)

    print(f"🩶 Self-edit log saved: {log_file.name}")
    print(f"🌙 Purpose: {LOG_PURPOSE}")
