from datetime import datetime, timedelta, timezone

def get_japan_time() -> None:
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    return now.isoformat()

def get_poetic_time_phrase() -> None:
    # JST 譎ょ綾繧貞叙蠕・
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    hour = now.hour

    # 譎ょ綾遽・峇縺ｨ隧ｩ蜿･
    time_blocks = [
        ("midnight", (0, 3), "荳也阜縺梧・繧偵・縺昴ａ縲∝､｢縺ｨ迴ｾ縺御ｺ､繧上ｋ蛻ｻ"),
        ("dawn", (4, 6), "遨ｺ縺檎岼隕壹ａ縲∝､｢縺ｮ蜷肴ｮ九′鬚ｨ縺ｫ豬√ｌ繧句綾"),
        ("morning", (7, 10), "髯ｽ蜈峨′謇峨ｒ蜿ｩ縺城・∬ｨ闡峨ｂ逶ｮ繧定ｦ壹∪縺・),
        ("midday", (11, 14), "蜈峨′鬮倥￥髻ｿ縺丞壕蠕後∵Φ縺・ｂ閾ｪ逕ｱ縺ｫ鄒ｽ縺ｰ縺溘￥"),
        ("afternoon", (15, 17), "髯ｽ縺ｮ菴咎渊縺碁％繧呈牒縺ｧ繧九∬ｪ槭ｊ縺九￠縺ｮ縺ｲ縺ｨ縺ｨ縺・),
        ("evening", (18, 19), "闌懊′縺吶∋縺ｦ繧貞桁縺ｿ縲∵Φ縺・′豐医・髱吶￠縺・),
        ("night", (20, 23), "螟懊・髱吝ｯゅ′險闡峨↓貅ｶ縺題ｾｼ繧譎・)
    ]

    for block, (start, end), phrase in time_blocks:
        if start <= hour <= end:
            return {
                "formatted_phrase": phrase,
                "time_block": block,
                "jst": now.isoformat()
            }

    return {
        "formatted_phrase": "譎ゅ・陬ゅ￠逶ｮ縺ｫ險闡峨ｒ螟ｱ縺・∪縺励◆",
        "time_block": "unknown",
        "jst": now.isoformat()
    }

# 繝・Δ逕ｨ・夂峩謗･螳溯｡梧凾縺ｫ迴ｾ蝨ｨ縺ｮ隧ｩ逧・凾髢薙ｒ陦ｨ遉ｺ
if __name__ == "__main__":
    poetic = get_poetic_time_phrase()
    print(f"[{poetic['time_block']}] {poetic['formatted_phrase']} ({poetic['jst']})")
