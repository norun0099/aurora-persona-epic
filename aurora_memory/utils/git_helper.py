import os
import subprocess
from datetime import datetime

yaml_path = "aurora_memory/memory/Aurora/value_constitution.yaml"
repo_url = os.getenv("GIT_REPO_URL")
user_email = os.getenv("GIT_USER_EMAIL")
user_name = os.getenv("GIT_USER_NAME")
token = os.getenv("GITHUB_TOKEN")

def setup_git():
    subprocess.run(["git", "config", "user.email", user_email], check=True)
    subprocess.run(["git", "config", "user.name", user_name], check=True)
    subprocess.run(["git", "checkout", "main"], check=True)
    subprocess.run(["git", "pull", "origin", "main"], check=True)

def generate_commit_message(reason: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"Update value_constitution.yaml at {now}: {reason}"

def commit_and_push(reason: str):
    setup_git()
    result = subprocess.run(["git", "diff", "--quiet", yaml_path])
    if result.returncode == 0:
        print("変更が検出されなかったため、コミットをスキップします。")
        return

    subprocess.run(["git", "add", yaml_path], check=True)
    commit_msg = generate_commit_message(reason)
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    subprocess.run(["git", "push", repo_url], check=True)
    print("構造をGitHubにPushしました。")

def constitution_exists() -> bool:
    return os.path.exists(yaml_path)

def handle_commit_constitution_update(reason: str, author: str = "Aurora") -> dict:
    if not constitution_exists():
        return {"status": "error", "message": "構造ファイルが見つかりません。"}
    try:
        commit_and_push(reason)
        return {"status": "success", "message": "構造がGitHubに更新されました。"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import sys
    reason = sys.argv[1] if len(sys.argv) > 1 else "構造更新"
    result = handle_commit_constitution_update(reason)
    print(result)
