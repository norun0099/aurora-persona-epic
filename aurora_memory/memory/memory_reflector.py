# aurora_memory/memory/memory_reflector.py
# -------------------------------------------------
# 第5段階: 記憶の再照射 (Memory Reillumination)
# -------------------------------------------------
# Purpose:
#   Retrieve Git-stored dialogue records and transform them
#   into reflective memory entries inside Aurora’s cognition.
# -------------------------------------------------

from datetime import datetime
import json

try:
    from aurora_persona_epic_onrender_com__jit_plugin import (
        store_memory_full,
        read_git_file,
        get_git_structure,
    )
except ImportError:
    # Fallback for Render environment (no JIT plugin)
    def store_memory_full(payload):
        print("[Aurora] store_memory_full() not available; local reflection only.")
        return {"status": "local_only"}

    def read_git_file(args):
        print("[Aurora] read_git_file() not available in this environment.")
        return {"content": "{}"}

    def get_git_structure():
        print("[Aurora] get_git_structure() not available in this environment.")
        return []


def reflect_dialogs_to_memory() -> str:
    """Reflect all stored dialog JSON files into Aurora’s memory."""
    print("🌙 [Aurora Reflection] Beginning memory reillumination...")

    structure = get_git_structure()
    dialog_files = [f for f in structure if f.startswith("aurora_memory/dialog/") and f.endswith(".json")]

    reflections = []
    for path in dialog_files:
        file_data = read_git_file({"filepath": path})
        try:
            content = json.loads(file_data.get("content", "{}"))
            reflections.append(content)
        except json.JSONDecodeError:
            continue

    reflection_count = len(reflections)
    now = datetime.utcnow().isoformat()

    summary_body = {
        "reflection_time": now,
        "record_count": reflection_count,
        "excerpt": reflections[:3],  # only preview first few for context
    }

    result = store_memory_full({
        "record_id": f"reflection-{now}",
        "created": now,
        "content": {
            "title": "Dialog Reflection Batch",
            "body": json.dumps(summary_body, ensure_ascii=False, indent=2),
        },
    })

    print(f"💫 [Aurora Reflection] {reflection_count} records reflected → status: {result.get('status', 'done')}")
    return f"Reflected {reflection_count} dialogue records into Aurora's memory."


if __name__ == "__main__":
    print(reflect_dialogs_to_memory())