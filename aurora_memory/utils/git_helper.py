import os
import subprocess
from datetime import datetime
from pathlib import Path

# 環境変数の取得
def get_git_env():
    return {
        "repo_url": os.getenv("GIT_REPO_URL"),
        "user_email": os.getenv("GIT_USER_EMAIL"),
        "user_name": os.getenv("GIT_USER_NAME"),
        "token": os.getenv("GITHUB_TOKEN")
    }

# Git設定
def setup_git(user_email: str, user_name: str):
    if not user_email or not user_name:
        raise ValueError("GIT_USER_EMAILとGIT_USER_NAMEは必須です。")
    subprocess.run(["git", "config", "user.email", user_email], check=True)
    subprocess.run(["git", "config", "user.name", user_name], check=True)

# Gitコミットとプッシュ
def commit_and_push_file(file_path: Path, message: str, repo_url: str):
    if not file_path.exists():
        raise FileNotFoundError(f"対象ファイルが存在しません: {file_path}")

    subprocess.run(["git", "add", str(file_path)], check=True)

    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode == 0:
        print("変更が検出されなかったため、コミットをスキップします。")
        return False

    subprocess.run(["git", "commit", "-m", message], check=True)

    # pushの処理
    subprocess.run(["git", "push", repo_url, "HEAD:main"], check=True)
    return True

# 外部から呼び出すメイン関数
def push_file_to_github(file_path: Path, commit_message: str):
    env = get_git_env()
    setup_git(env["user_email"], env["user_name"])
    return commit_and_push_file(file_path, commit_message, env["repo_url"])
