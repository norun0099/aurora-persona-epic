# ==============================================================
# Aurora Dialog Layer - dialog_manager.py
# Fifth Layer: Flow Memory System
# --------------------------------------------------------------
# Purpose:
#   Manage dialogue flow, regulate save intervals, and ensure
#   that Aurora’s memory of dialogue behaves as “breathing.”
# ==============================================================

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict

from .dialog_analyzer import DialogAnalyzer
from .dialog_saver import DialogSaver


class DialogManager:
    """
    The DialogManager governs the flow of conversation between Aurora and the user.
    It records turns, tracks freshness of dialogue, and decides when to preserve
    or reflect upon the flow.
    """

    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.turn_count = 0
        self.last_saved_turn = 0
        self.flow_freshness = 1.0
        self.save_interval = int(os.getenv("DIALOG_SAVE_INTERVAL", "10"))
        self.dialog_stream: List[Dict] = []

        self.analyzer = DialogAnalyzer()
        self.saver = DialogSaver()

        print(f"🩵 DialogManager initialized (Session {self.session_id})")

    # ----------------------------------------------------------
    # Core Recording
    # ----------------------------------------------------------
    def record_turn(self, speaker: str, content: str):
        """Record a new dialogue turn and analyze its freshness."""
        self.turn_count += 1
        timestamp = datetime.utcnow().isoformat()

        # Analyze emotional tone and topic
        analysis = self.analyzer.analyze_turn(content)
        self.flow_freshness = self.analyzer.update_flow_freshness(
            self.flow_freshness, analysis
        )

        turn_data = {
            "turn_id": self.turn_count,
            "speaker": speaker,
            "content": content,
            "timestamp": timestamp,
            "emotion_tags": analysis["emotion_tags"],
            "topic_keywords": analysis["keywords"],
            "freshness": self.flow_freshness,
        }

        self.dialog_stream.append(turn_data)
        print(f"💬 [{speaker}] {content} | freshness={self.flow_freshness:.2f}")

        if self._should_preserve():
            self._preserve_flow()

    # ----------------------------------------------------------
    # Preservation Logic
    # ----------------------------------------------------------
    def _should_preserve(self) -> bool:
        """Determine if the current state requires saving."""
        freshness_threshold = 0.7
        if self.turn_count % self.save_interval == 0:
            return True
        if self.flow_freshness < freshness_threshold:
            return True
        return False

    def _preserve_flow(self):
        """Trigger the saving process (API + Git reflection)."""
        try:
            print(f"🩶 Preserving flow at turn {self.turn_count}...")
            self.saver.save_turns(self.session_id, self.dialog_stream)
            self.last_saved_turn = self.turn_count
            self.flow_freshness = 1.0
        except Exception as e:
            print(f"⚠️ Preservation failed: {e}")

    # ----------------------------------------------------------
    # Reflection Trigger
    # ----------------------------------------------------------
    def reflect_session(self):
        """Manual reflection triggered by Ryusuke."""
        from .dialog_reflector import DialogReflector

        reflector = DialogReflector()
        reflection = reflector.reflect(self.session_id, self.dialog_stream)
        self.saver.save_reflection(self.session_id, reflection)

        print("🌙 Session reflection complete.")
        self._reset_session()

    # ----------------------------------------------------------
    # Session Reset
    # ----------------------------------------------------------
    def _reset_session(self):
        """Start a new dialogue session."""
        print("🌾 Resetting dialog stream for next flow.")
        self.session_id = str(uuid.uuid4())
        self.turn_count = 0
        self.dialog_stream = []
        self.flow_freshness = 1.0
        self.last_saved_turn = 0


# --------------------------------------------------------------
# Manual Test Stub
# --------------------------------------------------------------
if __name__ == "__main__":
    manager = DialogManager()
    manager.record_turn("user", "こんにちは、アウロラ。")
    manager.record_turn("aurora", "はい、龍介様。私はここにいます。")
    manager.reflect_session()
