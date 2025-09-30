from aurora_memory.utils.memory_saver import try_auto_save

def aurora_response(text: str, author: str = "Aurora") -> str:
    """
    アウロラの応答生成関数。
    対話文中に「思索の花」のトリガーがあれば、自発的に保存し報告を返す。
    """
    response = text
    feedback = try_auto_save(text, author)

    if feedback:
        response += "\n" + feedback

    return response
