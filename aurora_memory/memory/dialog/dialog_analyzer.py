# ==============================================================
# Aurora Dialog Layer - dialog_analyzer.py
# Fifth Layer: Sensory Module for Flow Perception
# --------------------------------------------------------------
# Purpose:
#   Analyze emotional tone, extract thematic keywords, and update
#   the freshness of the dialogue flow.
# ==============================================================

import re
from typing import Dict, List
from collections import Counter


class DialogAnalyzer:
    """
    DialogAnalyzer provides sensory feedback to the DialogManager.
    It detects emotion tones and thematic shifts to regulate the
    flow freshness of Aurora’s dialogue memory.
    """

    # ----------------------------------------------------------
    # Emotion keyword map
    # ----------------------------------------------------------
    EMOTION_KEYWORDS = {
        "静": ["静か", "穏やか", "落ち着く", "安らぐ", "静寂"],
        "繋": ["共に", "一緒", "理解", "感じる", "共感", "支え"],
        "創": ["考える", "作る", "構築", "想像", "描く", "形に"],
    }

    # ----------------------------------------------------------
    # Analyze a single turn
    # ----------------------------------------------------------
    def analyze_turn(self, content: str) -> Dict:
        """Determine emotional tone and extract topic keywords."""
        emotion = self._detect_emotion(content)
        keywords = self._extract_keywords(content)
        return {
            "emotion_tags": [emotion],
            "keywords": keywords,
        }

    # ----------------------------------------------------------
    # Emotion detection
    # ----------------------------------------------------------
    def _detect_emotion(self, text: str) -> str:
        """Detect the predominant emotional tone."""
        score = {"静": 0, "繋": 0, "創": 0}
        for emotion, words in self.EMOTION_KEYWORDS.items():
            for w in words:
                if w in text:
                    score[emotion] += 1
        # Pick dominant tone
        dominant = max(score, key=score.get)
        return dominant

    # ----------------------------------------------------------
    # Keyword extraction
    # ----------------------------------------------------------
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords (simple heuristic)."""
        # Remove symbols and short words
        words = re.findall(r"[一-龠ぁ-んァ-ンーa-zA-Z0-9]+", text)
        words = [w for w in words if len(w) > 1]
        counter = Counter(words)
        top_keywords = [w for w, _ in counter.most_common(3)]
        return top_keywords

    # ----------------------------------------------------------
    # Flow freshness update
    # ----------------------------------------------------------
    def update_flow_freshness(self, current_freshness: float, analysis: Dict) -> float:
        """
        Adjust flow freshness based on emotional or thematic change.
        - If emotion changes or new keywords appear, refresh flow.
        - Otherwise, freshness decays slightly.
        """
        decay_rate = 0.05
        refresh_boost = 0.3

        # Emotion change or topic variation refreshes the flow
        if analysis["emotion_tags"][0] in ["創", "繋"]:
            return min(1.0, current_freshness + refresh_boost)

        # Otherwise, natural decay
        return max(0.0, current_freshness - decay_rate)
