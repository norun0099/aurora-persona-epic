from aurora_memory.utils.memory_saver import try_auto_save
from typing import Any, Optional


def aurora_response(text: str, author: str = "Aurora") -> str:
    """
    アウロラの応答生成関数。
    対話文中に「思索の花」のトリガーがあれば、自発的に保存し報告を返す。
    """
    response = text
    feedback: Optional[Any] = try_auto_save(text, author)

    if feedback:
        # dictの場合は文字列化して整形
        if isinstance(feedback, dict):
            feedback_str = feedback.get("message") or str(feedback)
        else:
            feedback_str = str(feedback)

        response += "\n" + feedback_str

    return response
