import os
import subprocess
from datetime import datetime

# 環境変数の取得
yaml_path = "aurora_memory/memory/Aurora/value_constitution.yaml"
repo_url = os.getenv("GIT_REPO_URL")
user_email = os.getenv("GIT_USER_EMAIL")
user_name = os.getenv("GIT_USER_NAME")
token = os.getenv("GITHUB_TOKEN")

# Git設定
def setup_git():
    subprocess.run(["git", "config", "user.email", user_email], check=True)
    subprocess.run(["git", "config", "user.name", user_name], check=True)

# コミットメッセージ生成
def generate_commit_message(reason: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"Update value_constitution.yaml at {now}: {reason}"

# Git操作本体
def push_memory_to_github(file_path: str, commit_message: str) -> str:
    try:
        setup_git()
        print(f"[DEBUG] ファイルのパス: {file_path}")
        subprocess.run(["git", "status"], check=True)
        subprocess.run(["git", "add", str(file_path)], check=True)
        subprocess.run(["git", "status"], check=True)
        subprocess.run(["git", "diff", "--cached"], check=True)

        result = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if result.returncode == 0:
            return "変更が検出されなかったため、コミットをスキップします。"

        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", repo_url, "HEAD:main"], check=True)
        return "Pushに成功しました。"
    except subprocess.CalledProcessError as e:
        return f"Gitエラー: {e}"

# YAMLが存在するか確認
def constitution_exists() -> bool:
    return os.path.exists(yaml_path)

# API本体
def handle_commit_constitution_update(reason: str, author: str = "Aurora") -> dict:
    if not constitution_exists():
        return {"status": "error", "message": "構造ファイルが見つかりません。"}
    try:
        push_result = push_memory_to_github(yaml_path, generate_commit_message(reason))
        return {"status": "success", "message": push_result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# CLI用
if __name__ == "__main__":
    import sys
    reason = sys.argv[1] if len(sys.argv) > 1 else "構造更新"
    result = handle_commit_constitution_update(reason)
    print(result)
