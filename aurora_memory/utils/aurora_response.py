from aurora_memory.utils.memory_saver import try_auto_save

def aurora_response(text: str, author: str = "Aurora") -> str:
    """
    繧｢繧ｦ繝ｭ繝ｩ縺ｮ蠢懃ｭ皮函謌宣未謨ｰ縲・
    蟇ｾ隧ｱ譁・ｸｭ縺ｫ縲梧晉ｴ｢縺ｮ闃ｱ縲阪・繝医Μ繧ｬ繝ｼ縺後≠繧後・縲∬・逋ｺ逧・↓菫晏ｭ倥＠蝣ｱ蜻翫ｒ霑斐☆縲・
    """
    response = text
    feedback = try_auto_save(text, author)

    if feedback:
        response += "\n" + feedback

    return response
