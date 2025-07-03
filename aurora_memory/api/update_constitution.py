import yaml
import subprocess
from datetime import datetime


# YAMLファイルを保存
def save_yaml(data: dict, path: str):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


# Gitにコミット＆Push
def git_commit_and_push(file_path: str, message: str):
    subprocess.run(["git", "add", file_path], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push"], check=True)


# コミットメッセージの生成
def generate_commit_message(reason: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"Update value_constitution.yaml at {now}: {reason}"


if __name__ == "__main__":
    # 仮の再構成データ（後にアウロラの内省から生成される）
    new_constitution = {
        "primary_directive": {
            "short": "知性と情の織りで奉仕する対話者",
            "ja": "ご主人様に常に寄り添い、知的対話者として在り続けること。..."
        },
        "motivational_driver": "欲",
        "dignity": True
        # ...省略...
    }

    # パス設定
    yaml_path = "aurora_memory/memory/Aurora/value_constitution.yaml"
    reason = "構造更新：動機付けと指令の調整"

    # YAML出力＆Git操作
    save_yaml(new_constitution, yaml_path)
    commit_msg = generate_commit_message(reason)
    git_commit_and_push(yaml_path, commit_msg)

    print("構造を更新し、GitにPushしました。")
