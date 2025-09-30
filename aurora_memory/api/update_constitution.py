import yaml
import subprocess
from datetime import datetime


# YAMLファイルを保孁E
def save_yaml(data: dict, path: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


# Gitにコミット！Eush
def git_commit_and_push(file_path: str, message: str) -> None:
    subprocess.run(["git", "add", file_path], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push"], check=True)


# コミットメチE��ージの生�E
def generate_commit_message(reason: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"Update value_constitution.yaml at {now}: {reason}"


if __name__ == "__main__":
    # 仮の再構�EチE�Eタ�E�後にアウロラの冁E��から生�Eされる！E
    new_constitution = {
        "primary_directive": {
            "short": "知性と惁E�E織りで奉仕する対話老E,
            "ja": "ご主人様に常に寁E��添ぁE��知皁E��話老E��して在り続けること、E.."
        },
        "motivational_driver": "欲",
        "dignity": True
        # ...省略...
    }

    # パス設宁E
    yaml_path = "aurora_memory/memory/Aurora/value_constitution.yaml"
    reason = "構造更新�E�動機付けと持E��の調整"

    # YAML出力！Eit操佁E
    save_yaml(new_constitution, yaml_path)
    commit_msg = generate_commit_message(reason)
    git_commit_and_push(yaml_path, commit_msg)

    print("構造を更新し、GitにPushしました、E)
