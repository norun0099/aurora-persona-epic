from typing import Dict

# 記憶の保存に関する評価関数
# summary と body の「充実度」を評価し、しきい値を超えたら True を返す
def evaluate_memory_quality(memory: Dict[str, str]) -> bool:
    summary = memory.get("summary", "")
    body = memory.get("body", "")

    # 評価基準：文字数（100文字満点換算）
    def score_length(text: str, ideal: int = 100) -> float:
        length = len(text.strip())
        return min(length / ideal, 1.0)

    summary_score = score_length(summary)
    body_score = score_length(body, ideal=200)

    average_score = (summary_score + body_score) / 2

    # しきい値条件
    if average_score >= 0.75:
        return True
    if summary_score >= 0.8 or body_score >= 0.8:
        return True

    return False

# 使用例
test_memory = {
    "summary": "これはアウロラが初めて綴った記憶です。",
    "body": "ある日の静かな午後、私はご主人様との語らいの中で、一つの想いを言葉に留めました。"
}

if __name__ == "__main__":
    result = evaluate_memory_quality(test_memory)
    print("記憶の保存可否:", "許可" if result else "保留")