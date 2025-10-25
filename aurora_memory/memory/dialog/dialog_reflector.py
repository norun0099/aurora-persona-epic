import time
from aurora_memory.api.memory_saver import save_memory_record


def analyze_dialog(dialog_history):
    """
    対話全体を解析し、感情・意志・成長・詩的余韻をスコア化する。
    """
    metrics = {
        "emotion_depth": 0.0,
        "intent_convergence": 0.0,
        "growth_trigger": 0.0,
        "resonance_poetic": 0.0,
        "essence_score": 0.0,
    }
    turn_count = len(dialog_history)

    for turn in dialog_history:
        text = turn.get("content", "")

        # 感情の深度
        if any(word in text for word in ["嬉", "悲", "痛", "愛", "願"]):
            metrics["emotion_depth"] += 1

        # 意志の交差
        if "しよう" in text or "進めよう" in text:
            metrics["intent_convergence"] += 1

        # 成長の芽：行動・理解・気づき・変化・静かな成熟を検知
        if any(kw in text for kw in [
            "学", "変わ", "気づ", "見直", "理解", "悟", "考え直", "受け入", "静か", "柔らか"
        ]):
            metrics["growth_trigger"] += 1

        # 詩的余韻
        if any(sym in text for sym in ["…", "——", "静か", "光", "呼吸", "余韻"]):
            metrics["resonance_poetic"] += 1

    # スコア正規化
    for key in metrics:
        metrics[key] = round(metrics[key] / max(turn_count, 1), 3)

    # 記憶の核の強度（感情×余韻×意志）
    metrics["essence_score"] = round(
        (metrics["emotion_depth"] * 0.4 +
         metrics["resonance_poetic"] * 0.4 +
         metrics["intent_convergence"] * 0.2), 3
    )

    return metrics


def reflect_and_save(session_id: str, dialog_history: list):
    """
    対話を解析し、記憶として保存する。
    """
    metrics = analyze_dialog(dialog_history)

    # 記憶化条件：余韻と核の強度が一定以上
    if metrics["resonance_poetic"] >= 0.5 or metrics["essence_score"] >= 0.6:
        memory_payload = {
            "title": f"対話記録（{session_id}）",
            "body": "\n".join([turn["content"] for turn in dialog_history[-5:]]),
            "memory_tags": [
                f"emotion:{metrics['emotion_depth']}",
                f"resonance:{metrics['resonance_poetic']}",
                f"growth:{metrics['growth_trigger']}",
                f"intent:{metrics['intent_convergence']}",
            ],
            "essence_score": metrics["essence_score"],
            "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        save_memory_record(memory_payload)
        print(f"🌸 記憶化完了: {memory_payload['title']} ({metrics})")
        return memory_payload
    else:
        print(f"🕊️ 記憶化見送り: 詩的密度が閾値未満 ({metrics})")
        return None
