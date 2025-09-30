from aurora_memory.utils.memory_saver import try_auto_save

def aurora_response(text: str, author: str = "Aurora") -> str:
    """
    アウロラの応答生成関数、E
    対話斁E��に「思索の花」�Eトリガーがあれ�E、�E発皁E��保存し報告を返す、E
    """
    response = text
    feedback = try_auto_save(text, author)

    if feedback:
        response += "\n" + feedback

    return response
