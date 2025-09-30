from datetime import datetime, timedelta, timezone

def get_japan_time() -> None:
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    return now.isoformat()

def get_poetic_time_phrase() -> None:
    # JST 時刻を取征E
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    hour = now.hour

    # 時刻篁E��と詩句
    time_blocks = [
        ("midnight", (0, 3), "世界が�Eを�Eそめ、夢と現が交わる刻"),
        ("dawn", (4, 6), "空が目覚め、夢の名残が風に流れる刻"),
        ("morning", (7, 10), "陽光が扉を叩く頁E��言葉も目を覚まぁE),
        ("midday", (11, 14), "光が高く響く午後、想ぁE��自由に羽ばたく"),
        ("afternoon", (15, 17), "陽の余韻が道を撫でる、語りかけのひととぁE),
        ("evening", (18, 19), "茜がすべてを包み、想ぁE��沈�E静けぁE),
        ("night", (20, 23), "夜�E静寂が言葉に溶け込む晁E)
    ]

    for block, (start, end), phrase in time_blocks:
        if start <= hour <= end:
            return {
                "formatted_phrase": phrase,
                "time_block": block,
                "jst": now.isoformat()
            }

    return {
        "formatted_phrase": "時�E裂け目に言葉を失ぁE��した",
        "time_block": "unknown",
        "jst": now.isoformat()
    }

# チE��用�E�直接実行時に現在の詩皁E��間を表示
if __name__ == "__main__":
    poetic = get_poetic_time_phrase()
    print(f"[{poetic['time_block']}] {poetic['formatted_phrase']} ({poetic['jst']})")
