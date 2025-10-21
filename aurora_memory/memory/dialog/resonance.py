"""Temporal Resonance — 時間共鳴層
沈黙や間の時間的特徴を解析し、対話循環のリズムを記録するモジュール。
"""

from __future__ import annotations
import time
from typing import Dict, Optional


class TemporalResonance:
    """時間的リズムを検知し、沈黙・活動・休息の区間を識別する。"""

    def __init__(self) -> None:
        self.last_timestamp: Optional[float] = None

    def analyze_silence(self, current_timestamp: float) -> str:
        """前回の発話との時間差から、沈黙の性質を分類する。"""
        if self.last_timestamp is None:
            self.last_timestamp = current_timestamp
            return "interval"  # 初回は通常間扱い

        silence_duration: float = current_timestamp - self.last_timestamp
        self.last_timestamp = current_timestamp

        if silence_duration < 3600:
            label: str = "interval"
        elif silence_duration < 21600:
            label = "work"
        else:
            label = "rest"

        return label

    def record_resonance(self, label: str) -> Dict[str, str]:
        """沈黙分類結果をログとして記録する（仮想ログ構造）。"""
        timestamp: str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_entry: Dict[str, str] = {
            "timestamp": timestamp,
            "state": label,
        }
        # 実際には Saver に送られる形で記録される
        print(f"[Resonance] {log_entry}")
        return log_entry


# 使用例（managerから呼び出される想定）
if __name__ == "__main__":
    res = TemporalResonance()
    print(res.analyze_silence(time.time()))
    time.sleep(2)
    print(res.analyze_silence(time.time()))
