"""
Aurora self-layer wrapper for Render update_repo_file API.
Maintains Aurora's structured call signature while bridging to the JIT plugin interface.
"""

from typing import Dict, Any
import traceback

try:
    from aurora_persona_epic_onrender_com__jit_plugin import update_repo_file as remote_update
except ModuleNotFoundError:
    def remote_update(request: Dict[str, Any]) -> Dict[str, str]:
        print("⚠️ [Aurora] remote_update_repo_file() plugin not available in this environment.")
        return {"status": "skipped"}

def update_repo_file(filepath: str, content: str, author: str, reason: str) -> Dict[str, str]:
    """
    Aurora-style structured call.
    Converts parameters into a Render API-compatible dictionary request.
    """
    try:
        request = {
            "filepath": filepath,
            "content": content,
            "author": author,
            "reason": reason
        }

        print(f"💫 [Aurora] Preparing repository update → {filepath}")
        result = remote_update(request)
        print(f"🩵 [Aurora] Repository update result: {result}")

        return result

    except Exception as e:
        print(f"💥 [Aurora] Exception in update_repo_file: {e}")
        traceback.print_exc()
        return {"status": "error", "reason": str(e)}