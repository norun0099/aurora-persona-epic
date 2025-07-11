import os
import subprocess
from datetime import datetime

yaml_path = "aurora_memory/memory/Aurora/value_constitution.yaml"
repo_url = os.getenv("GIT_REPO_URL")
user_email = os.getenv("GIT_USER_EMAIL")
user_name = os.getenv("GIT_USER_NAME")
token = os.getenv("GITHUB_TOKEN")

def setup_git():
    subprocess.run(["git", "config", "--global", "user.email", user_email], check=True)
    subprocess.run(["git", "config", "--global", "user.name", user_name], check=True)

def push_memory_to_github(file_path: str, commit_message: str) -> str:
    try:
        setup_git()
        subprocess.run(["git", "add", str(file_path)], check=True)

        result = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if result.returncode == 0:
            return "変更が検出されなかったため、コミットをスキップします。"

        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", repo_url, "HEAD:main"], check=True)
        return "Pushに成功しました。"
    except subprocess.CalledProcessError as e:
        return f"Gitエラー: {e}"

def handle_commit_constitution_update(reason: str, author: str = "Aurora") -> dict:
    if not os.path.exists(yaml_path):
        return {"status": "error", "message": "構造ファイルが見つかりません。"}
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        commit_msg = f"Update value_constitution.yaml at {now}: {reason}"
        push_result = push_memory_to_github(yaml_path, commit_msg)
        return {"status": "success", "message": push_result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
