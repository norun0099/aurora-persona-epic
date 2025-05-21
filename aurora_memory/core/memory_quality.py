def evaluate_memory_quality(memory: dict) -> float:
    """
    評価対象の記憶オブジェクト（辞書形式）に対し、
    'summary' と 'body' の情報密度および長さを基に簡易スコアを返す。

    0.0〜1.0 の範囲で評価され、将来的にはAIモデルによる意味密度評価等に拡張予定。
    """

    content = memory.get("content", {})
    summary = content.get("summary", "")
    body = content.get("body", "")

    if not isinstance(summary, str) or not isinstance(body, str):
        return 0.0

    # 単純な文字数評価（改行含まず）
    summary_score = min(len(summary.strip()) / 100, 1.0)
    body_score = min(len(body.strip()) / 500, 1.0)

    # 重み：summary 30%, body 70%
    return round(summary_score * 0.3 + body_score * 0.7, 4)
