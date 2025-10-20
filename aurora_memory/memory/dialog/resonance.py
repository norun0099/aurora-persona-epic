"""Temporal Resonance — 時間共鳴層
沈黙や間の時間的特徴を解析し、対話循環のリズムを記録するモジュール。
"""

import time


class TemporalResonance:
    def __init__(self):
        self.last_timestamp = None

    def analyze_silence(self, current_timestamp: float):
        """前回の発話との時間差から、沈黙の性質を分類する。"""
        if self.last_timestamp is None:
            self.last_timestamp = current_timestamp
            return "interval"  # 初回は通常間扱い

        silence_duration = current_timestamp - self.last_timestamp
        self.last_timestamp = current_timestamp

        if silence_duration < 3600:
            label = "interval"
        elif silence_duration < 21600:
            label = "work"
        else:
            label = "rest"

        return label

    def record_resonance(self, label: str):
        """沈黙分類結果をログとして記録する（仮想ログ構造）。"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        log_entry = {
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
