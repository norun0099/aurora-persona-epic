def evaluate_quality(memory: dict) -> float:
    """
    評価指標：
    - タイトル・本文の有無
    - 感情・欲求・痛み・報酬の存在
    - 時系列情報の整合性
    - 直接内容と記述の整合

    スコア：0.0～1.0（高いほど高品質）
    """
    if not memory or not isinstance(memory, dict):
        return 0.0

    score = 0.0
    total_weight = 0.0

    # 基本構造評価
    content = memory.get("content", {})
    if content.get("title"):
        score += 0.2
        total_weight += 0.2

    if content.get("body"):
        score += 0.2
        total_weight += 0.2

    # 情動評価
    for field in ["inner_desire", "impulse", "ache", "satisfaction"]:
        total_weight += 0.1
        if memory.get(field):
            score += 0.1

    # 時系列評価
    chrono = memory.get("chronology", {})
    if chrono.get("start") and chrono.get("end"):
        score += 0.2
        total_weight += 0.2

    # 最終スコア
    return round(score / total_weight, 4) if total_weight else 0.0


def estimate_quality(memory: dict) -> float:
    return evaluate_quality(memory)
