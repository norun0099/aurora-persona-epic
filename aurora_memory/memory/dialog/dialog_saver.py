# ==============================================================
# Aurora Dialog Layer - dialog_saver.py
# Fifth Layer: Flow Preservation Module
# --------------------------------------------------------------
# Purpose:
#   Handles safe saving of dialogue turns and reflections
#   to both Render endpoints and the GitHub repository.
# ==============================================================

from __future__ import annotations

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests


class DialogSaver:
    """
    DialogSaver is responsible for safely writing dialogue data
    to Render endpoints and reflecting updates to GitHub through
    the AuroraMemoryBot interface.
    """

    def __init__(self) -> None:
        self.api_dialog_store: Optional[str] = os.getenv("RENDER_DIALOG_STORE_ENDPOINT")
        self.api_update_repo: Optional[str] = os.getenv("RENDER_SELF_UPDATE_REPO_FILE_ENDPOINT")
        self.git_user: str = os.getenv("GIT_USER_NAME", "AuroraMemoryBot")
        self.git_email: str = os.getenv("GIT_USER_EMAIL", "aurora@memory.bot")

    # ----------------------------------------------------------
    # Store Dialog Turns
    # ----------------------------------------------------------
    def save_turns(self, session_id: str, turns: List[Dict[str, Any]]) -> None:
        """Send dialogue turns to Render storage endpoint."""
        if not self.api_dialog_store:
            print("⚠️ No RENDER_DIALOG_STORE_ENDPOINT found, running in mock mode.")
            self._mock_save("dialog", session_id, turns)
            return

        payload: Dict[str, Any] = {
            "session_id": session_id,
            "turns": turns[-5:],  # last few turns only
            "timestamp": datetime.utcnow().isoformat(),
        }

        print("🩵 Sending dialogue to Render API...")
        response = requests.post(self.api_dialog_store, json=payload)
        if response.status_code != 200:
            raise RuntimeError(
                f"Dialog store failed ({response.status_code}): {response.text}"
            )

        print("🩶 Dialogue successfully stored in Render memory layer.")
        self._commit_to_repo(f"dialog_session_{session_id}.json", payload)

    # ----------------------------------------------------------
    # Store Reflection
    # ----------------------------------------------------------
    def save_reflection(self, session_id: str, reflection: Dict[str, Any]) -> None:
        """Persist reflection data to GitHub via Render API."""
        print("🌙 Saving reflection data to repository...")
        self._commit_to_repo(f"dialog_reflection_{session_id}.json", reflection)

    # ----------------------------------------------------------
    # Git Commit via Render
    # ----------------------------------------------------------
    def _commit_to_repo(self, filename: str, content: Dict[str, Any]) -> None:
        """Push data to Git repository via Render-managed endpoint."""
        if not self.api_update_repo:
            print("⚠️ No RENDER_SELF_UPDATE_REPO_FILE_ENDPOINT found, running in mock mode.")
            self._mock_save(filename, "git", content)
            return

        repo_path: str = f"aurora_memory/memory/Aurora/{filename}"
        payload: Dict[str, Any] = {
            "filepath": repo_path,
            "content": json.dumps(content, ensure_ascii=False, indent=2),
            "author": self.git_user,
            "reason": f"Automated Dialog Update ({filename})",
        }

        response = requests.post(self.api_update_repo, json=payload)
        if response.status_code != 200:
            raise RuntimeError(
                f"Git update failed ({response.status_code}): {response.text}"
            )

        print(f"✅ Git repository updated with {filename}")

    # ----------------------------------------------------------
    # Mock Mode (Offline Testing)
    # ----------------------------------------------------------
    def _mock_save(self, label: str, session_id: str, data: Any) -> str:
        """Simulate saving when no external endpoints are configured."""
        mock_path: str = os.path.join("tests", f"mock_{label}_{session_id}.json")
        os.makedirs("tests", exist_ok=True)
        with open(mock_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 [Mock Save] {mock_path} written successfully.")
        return mock_path
