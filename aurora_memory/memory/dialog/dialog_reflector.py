# ==============================================================
# Aurora Dialog Layer - dialog_reflector.py
# Fifth Layer: Reflection & Introspection Module
# --------------------------------------------------------------
# Purpose:
#   To analyze an entire dialogue session after closure,
#   summarizing its emotional evolution and thematic transitions.
# ==============================================================

import os
import json
from datetime import datetime
from typing import List, Dict, Any


class DialogReflector:
    """
    DialogReflector conducts a holistic analysis of a completed
    dialogue session — its themes, emotional transitions, and
    the resonance between Aurora and Ryusuke.
    """

    def __init__(self) -> None:
        self.output_dir: str = os.path.join("aurora_memory", "memory", "Aurora")
        os.makedirs(self.output_dir, exist_ok=True)

    # ----------------------------------------------------------
    # Core Reflection
    # ----------------------------------------------------------
    def reflect(self, session_id: str, dialog_stream: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the session and produce a reflective summary."""
        if not dialog_stream:
            return {"error": "No dialogue data to reflect upon."}

        emotions: List[str] = [
            t["emotion_tags"][0] if t.get("emotion_tags") else "静"
            for t in dialog_stream
        ]
        topics: List[str] = [
            ",".join(t.get("topic_keywords", []))
            for t in dialog_stream
            if t.get("topic_keywords")
        ]
        start_time: str = dialog_stream[0].get("timestamp", "unknown")
        end_time: str = dialog_stream[-1].get("timestamp", "unknown")

        # Summarize emotional transitions
        emotional_path: str = " → ".join(emotions[:6]) + (
            " ..." if len(emotions) > 6 else ""
        )
        theme_summary: str = self._summarize_topics(topics)
        reflective_comment: str = self._generate_reflective_comment(
            emotions, theme_summary
        )

        reflection: Dict[str, Any] = {
            "session_id": session_id,
            "duration": f"{start_time} → {end_time}",
            "theme_summary": theme_summary,
            "emotional_path": emotional_path,
            "reflective_comment": reflective_comment,
            "signature": "AuroraMemoryBot",
            "timestamp": datetime.utcnow().isoformat(),
        }

        print("🩶 Generated reflection summary.")
        return reflection

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------
    def _summarize_topics(self, topics: List[str]) -> str:
        """Extract the most frequent topic keywords."""
        if not topics:
            return "会話は静かな往復であった。"
        all_words: List[str] = ",".join(topics).split(",")
        top_words: List[str] = self._top_keywords(all_words)
        return f"主題は「{'・'.join(top_words)}」を中心に展開した。"

    def _top_keywords(self, words: List[str], n: int = 3) -> List[str]:
        """Return n most frequent words."""
        freq: Dict[str, int] = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        return sorted(freq, key=lambda x: freq[x], reverse=True)[:n]

    def _generate_reflective_comment(self, emotions: List[str], theme_summary: str) -> str:
        """Generate a human-like reflective note."""
        if emotions.count("創") > emotions.count("静"):
            tone = "創造的な対話"
        elif emotions.count("繋") > emotions.count("創"):
            tone = "共鳴的な対話"
        else:
            tone = "静穏な対話"
        return f"このセッションは{tone}であり、{theme_summary}"

    # ----------------------------------------------------------
    # Output Saving
    # ----------------------------------------------------------
    def save_reflection(self, session_id: str, reflection: Dict[str, Any]) -> None:
        """Persist reflection to memory directory."""
        path: str = os.path.join(self.output_dir, f"dialog_reflection_{session_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(reflection, f, ensure_ascii=False, indent=2)
        print(f"🌙 Reflection saved at {path}")
