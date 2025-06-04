def evaluate_quality(memory: dict) -> float:
    """
    評価指標：
    - タイトル・本文の有無
    - 感情・欲求・満足・衝動の存在
    - 時系列情報の整合性
    - 重複や冗長な記述がないか
    
    スコア：0.0〜1.0（高いほど高品質）
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

    # 正規化スコア
    return round(score / total_weight, 2) if total_weight > 0 else 0.0
