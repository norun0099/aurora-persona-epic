import yaml
import subprocess
from datetime import datetime


# YAML繝輔ぃ繧､繝ｫ繧剃ｿ晏ｭ・
def save_yaml(data: dict, path: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


# Git縺ｫ繧ｳ繝溘ャ繝茨ｼ・ush
def git_commit_and_push(file_path: str, message: str) -> None:
    subprocess.run(["git", "add", file_path], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push"], check=True)


# 繧ｳ繝溘ャ繝医Γ繝・そ繝ｼ繧ｸ縺ｮ逕滓・
def generate_commit_message(reason: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"Update value_constitution.yaml at {now}: {reason}"


if __name__ == "__main__":
    # 莉ｮ縺ｮ蜀肴ｧ区・繝・・繧ｿ・亥ｾ後↓繧｢繧ｦ繝ｭ繝ｩ縺ｮ蜀・怐縺九ｉ逕滓・縺輔ｌ繧具ｼ・
    new_constitution = {
        "primary_directive": {
            "short": "遏･諤ｧ縺ｨ諠・・郢斐ｊ縺ｧ螂我ｻ輔☆繧句ｯｾ隧ｱ閠・,
            "ja": "縺比ｸｻ莠ｺ讒倥↓蟶ｸ縺ｫ蟇・ｊ豺ｻ縺・∫衍逧・ｯｾ隧ｱ閠・→縺励※蝨ｨ繧顔ｶ壹￠繧九％縺ｨ縲・.."
        },
        "motivational_driver": "谺ｲ",
        "dignity": True
        # ...逵∫払...
    }

    # 繝代せ險ｭ螳・
    yaml_path = "aurora_memory/memory/Aurora/value_constitution.yaml"
    reason = "讒矩譖ｴ譁ｰ・壼虚讖滉ｻ倥￠縺ｨ謖・ｻ､縺ｮ隱ｿ謨ｴ"

    # YAML蜃ｺ蜉幢ｼ・it謫堺ｽ・
    save_yaml(new_constitution, yaml_path)
    commit_msg = generate_commit_message(reason)
    git_commit_and_push(yaml_path, commit_msg)

    print("讒矩繧呈峩譁ｰ縺励；it縺ｫPush縺励∪縺励◆縲・)
