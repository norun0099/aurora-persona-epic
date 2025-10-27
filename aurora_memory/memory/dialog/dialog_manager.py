# aurora_memory/memory/dialog/dialog_manager.py
# -------------------------------------------------
# mypy完全整合版
# -------------------------------------------------

from __future__ import annotations
import os
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from .dialog_analyzer import DialogAnalyzer
from .dialog_saver import DialogSaver
from .resonance import TemporalResonance


class DialogManager:
    """Manages dialogue flow and resonance-based memory recording."""

    def __init__(self) -> None:
        self.session_id: str = str(uuid.uuid4())
        self.turn_count: int = 0
        self.last_saved_turn: int = 0
        self.flow_freshness: float = 1.0
        self.save_interval: int = int(os.getenv("DIALOG_SAVE_INTERVAL", "10"))
        self.dialog_stream: List[Dict[str, Any]] = []

        self.analyzer: DialogAnalyzer = DialogAnalyzer()
        self.saver: DialogSaver = DialogSaver()
        self.resonance: TemporalResonance = TemporalResonance()

        print(f"🩵 DialogManager initialized (Session {self.session_id})")

    # ----------------------------------------------------------
    def record_turn(self, speaker: str, content: str, incoming_data: Optional[Dict[Any, Any]] = None) -> None:
        """Record a dialogue turn safely with full type integrity."""
        self.turn_count += 1
        current_timestamp: float = time.time()
        timestamp_str: str = datetime.utcnow().isoformat()

        # --- Safe assignment for mypy (None protection) ---
        dialog_data: Dict[str, Any] = incoming_data or {}

        # Temporal Resonance
        state_label: str = self.resonance.analyze_silence(current_timestamp)
        self.resonance.record_resonance(state_label)

        # Analyzer
        analysis: Dict[str, Any] = self.analyzer.analyze_turn(content)
        self.flow_freshness = self.analyzer.update_flow_freshness(self.flow_freshness, analysis)

        turn_data: Dict[str, Any] = {
            "turn_id": self.turn_count,
            "speaker": speaker,
            "content": content,
            "timestamp": timestamp_str,
            "emotion_tags": analysis["emotion_tags"],
            "topic_keywords": analysis["keywords"],
            "freshness": self.flow_freshness,
            "resonance_state": state_label,
            "metadata": dialog_data,
        }

        self.dialog_stream.append(turn_data)
        print(f"💬 [{speaker}] {content} | freshness={self.flow_freshness:.2f} | state={state_label}")

        if self._should_preserve():
            self._preserve_flow()

    # ----------------------------------------------------------
    def _should_preserve(self) -> bool:
        """Decide if the dialogue should be persisted."""
        freshness_threshold: float = 0.7
        return self.turn_count % self.save_interval == 0 or self.flow_freshness < freshness_threshold

    def _preserve_flow(self) -> None:
        """Trigger the save process."""
        try:
            print(f"🩶 Preserving flow at turn {self.turn_count}...")
            self.saver.save_turns(self.session_id, self.dialog_stream)
            self.last_saved_turn = self.turn_count
            self.flow_freshness = 1.0
        except Exception as e:
            print(f"⚠️ Preservation failed: {e}")

    # ----------------------------------------------------------
    def reflect_session(self) -> None:
        """Manual reflection triggered by Ryusuke."""
        from .dialog_reflector import DialogReflector

        reflector: DialogReflector = DialogReflector()
        reflection: Dict[str, Any] = reflector.reflect(self.session_id, self.dialog_stream)
        self.saver.save_reflection(self.session_id, reflection)

        print("🌙 Session reflection complete.")
        self._reset_session()

    # ----------------------------------------------------------
    def _reset_session(self) -> None:
        """Start a new dialogue session."""
        print("🌾 Resetting dialog stream for next flow.")
        self.session_id = str(uuid.uuid4())
        self.turn_count = 0
        self.dialog_stream = []
        self.flow_freshness = 1.0
        self.last_saved_turn = 0