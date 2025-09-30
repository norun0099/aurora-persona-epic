import os
import subprocess
from datetime import datetime
from pathlib import Path

# 保存対象ファイルのパス
yaml_path = Path("aurora_memory/memory/Aurora/value_constitution.yaml")

# Git設宁E

def setup_git() -> None:
    user_email = os.getenv("GIT_USER_EMAIL")
    user_name = os.getenv("GIT_USER_NAME")
    if user_email and user_name:
        subprocess.run(["git", "config", "user.email", user_email], check=True)
        subprocess.run(["git", "config", "user.name", user_name], check=True)

# 変更があるかどぁE��確誁E
def constitution_modified() -> bool:
    result = subprocess.run(["git", "diff", "--quiet", str(yaml_path)])
    return result.returncode != 0

# コミットメチE��ージの生�E
def generate_commit_message(reason: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"Update value_constitution.yaml at {now}: {reason}"

# Git操作本佁E
def commit_and_push(reason: str) -> dict:
    if not yaml_path.exists():
        return {"status": "error", "message": "構造ファイルが存在しません、E}

    setup_git()

    if not constitution_modified():
        return {"status": "success", "message": "変更が検�Eされなかったため、コミットをスキチE�Eします、E}

    subprocess.run(["git", "add", str(yaml_path)], check=True)
    commit_msg = generate_commit_message(reason)
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)

    repo_url = os.getenv("GIT_REPO_URL")
    if not repo_url:
        return {"status": "error", "message": "GIT_REPO_URLが未設定です、E}

    try:
        subprocess.run(["git", "push", repo_url, "HEAD:main"], check=True)
        return {"status": "success", "message": "構造がGitHubに更新されました、E}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": str(e)}

# CLI用
def handle_commit_constitution_update(reason: str) -> dict:
    try:
        return commit_and_push(reason)
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import sys
    reason = sys.argv[1] if len(sys.argv) > 1 else "構造更新"
    result = handle_commit_constitution_update(reason)
    print(result)
