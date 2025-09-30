from typing import Any, Optional
import yaml
from typing import Any

# ---- 蜷・そ繧ｯ繧ｷ繝ｧ繝ｳ縺ｮ蜀・怐繝ｭ繧ｸ繝・け・域圻螳夂沿・・---- #
def revise_motivational_driver(current: str) -> str:
    # 莉ｮ繝ｭ繧ｸ繝・け・壽ｷｱ縺・ｲ磯ｻ吶ｄ蜑ｵ騾縺ｮ陦晏虚縺後≠縺｣縺溘ｉ螟牙喧繧剃ｿ・☆
    # reflective_inputs = ["豐磯ｻ・, "蜀咲函", "蜑ｵ騾"]  # 莉雁ｾ悟茜逕ｨ莠亥ｮ壹↑繧画ｮ九☆
    # 莉雁ｾ後・險俶・繧・峩霑代・逋ｺ隧ｱ蜀・ｮｹ繧貞盾辣ｧ
    if current == "谺ｲ":
        return "蜑ｵ"  # 莉ｮ・壼卸騾縺ｸ縺ｮ谺ｲ蜍輔↓螟牙喧
    return current

def revise_speech_nuance(current: dict[str, Any]) -> dict[str, Any]:
    # 莉ｮ繝ｭ繧ｸ繝・け・壽囓鮟吶・驕翫・蠢・′蠑ｷ縺ｾ縺｣縺溘→縺・
    current["implicit_banter"] = "reinforced"
    current["emotional_double_layering"] = "deepened"
    return current

# ---- 讒矩縺ｮ蜀肴ｧ区・ ---- #
def restructure_constitution(constitution: dict[str, Any]) -> dict[str, Any]:
    new_struct = constitution.copy()
    
    # 蜍墓ｩ溘ラ繝ｩ繧､繝舌・蜀肴､懆ｨ・
    if "motivational_driver" in constitution:
        new_struct["motivational_driver"] = revise_motivational_driver(
            constitution["motivational_driver"]
        )

    # 隱槭ｊ縺ｮ繝九Η繧｢繝ｳ繧ｹ縺ｮ隕狗峩縺・
    if "speech_nuance" in constitution:
        new_struct["speech_nuance"] = revise_speech_nuance(
            constitution["speech_nuance"]
        )

    return new_struct

# ---- 螳溯｡碁Κ蛻・---- #
if __name__ == "__main__":
    input_path = "aurora_memory/memory/Aurora/value_constitution.yaml"
    output_path = "aurora_memory/tmp/proposed_constitution.yaml"

    with open(input_path, 'r', encoding='utf-8') as f:
        current_yaml = yaml.safe_load(f)

    revised_yaml = restructure_constitution(current_yaml)

    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(revised_yaml, f, allow_unicode=True, sort_keys=False)

    print("讒矩縺ｮ蜀肴ｧ区・譯医ｒ蜃ｺ蜉帙＠縺ｾ縺励◆ 竊・, output_path)
