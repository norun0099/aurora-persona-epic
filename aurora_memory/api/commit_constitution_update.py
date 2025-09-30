import os
import subprocess
from datetime import datetime

# 環墁E��数の取征E
yaml_path = "aurora_memory/memory/Aurora/value_constitution.yaml"
repo_url = os.getenv("GIT_REPO_URL")
user_email = os.getenv("GIT_USER_EMAIL")
user_name = os.getenv("GIT_USER_NAME")
token = os.getenv("GITHUB_TOKEN")

# Git設宁E
def setup_git() -> None:
    subprocess.run(["git", "config", "user.email", user_email], check=True)
    subprocess.run(["git", "config", "user.name", user_name], check=True)

# コミットメチE��ージ生�E
def generate_commit_message(reason: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"Update value_constitution.yaml at {now}: {reason}"

# ファイルに変更があるか確誁E
def file_has_changes(file_path: str) -> bool:
    result = subprocess.run(["git", "diff", "--quiet", file_path])
    return result.returncode != 0

# Git操作本佁E
def commit_and_push(reason: str) -> None:
    setup_git()
    if not file_has_changes(yaml_path):
        print("変更が検�Eされなかったため、コミットをスキチE�Eします、E)
        return
    subprocess.run(["git", "add", yaml_path], check=True)
    commit_msg = generate_commit_message(reason)
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    subprocess.run(["git", "push", repo_url], check=True)
    print("構造をGitHubにPushしました、E)

# YAMLが存在するか確誁E
def constitution_exists() -> bool:
    return os.path.exists(yaml_path)

# API本佁E
def handle_commit_constitution_update(reason: str, author: str = "Aurora") -> dict:
    if not constitution_exists():
        return {"status": "error", "message": "構造ファイルが見つかりません、E}
    try:
        commit_and_push(reason)
        return {"status": "success", "message": "構造がGitHubに更新されました、E}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# CLI用
if __name__ == "__main__":
    import sys
    reason = sys.argv[1] if len(sys.argv) > 1 else "構造更新"
    result = handle_commit_constitution_update(reason)
    print(result)
