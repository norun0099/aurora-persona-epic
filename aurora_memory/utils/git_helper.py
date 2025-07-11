import os
import subprocess
from pathlib import Path
from typing import Optional


def ensure_git_initialized():
    """
    Gitのユーザー情報が設定されているかを確認し、設定されていなければ警告する。
    """
    user_email = os.environ.get("GIT_USER_EMAIL")
    user_name = os.environ.get("GIT_USER_NAME")
    if not user_email or not user_name:
        print("[Aurora Debug] WARNING: GIT_USER_EMAIL or GIT_USER_NAME is missing!")
        return False
    try:
        subprocess.run(["git", "config", "--global", "user.email", user_email], check=True)
        subprocess.run(["git", "config", "--global", "user.name", user_name], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print("[Aurora Debug] Git config failed:", str(e))
        return False


def push_whiteboard_to_github(file_path: Path, commit_message: Optional[str] = "Sync whiteboard from Render"):
    """
    Renderから取得したwhiteboardをGitHubへ同期（commit & push）する。
    """
    repo_url = os.environ.get("GIT_REPO_URL")
    token = os.environ.get("GITHUB_TOKEN")

    if not ensure_git_initialized():
        return {"status": "error", "message": "Git identity is missing or setup failed."}

    try:
        print(f"[Aurora Debug] Preparing to push {file_path}...")

        subprocess.run(["git", "checkout", "main"], check=True)
        subprocess.run(["git", "add", str(file_path)], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        if repo_url and token:
            repo_url_with_token = repo_url.replace("https://", f"https://{token}@")
            print("[Aurora Debug] Pushing to:", repo_url_with_token)
            subprocess.run(["git", "push", repo_url_with_token, "main"], check=True)
        else:
            subprocess.run(["git", "push", "origin", "main"], check=True)

        return {"status": "success", "message": "Whiteboard pushed to GitHub successfully."}

    except subprocess.CalledProcessError as e:
        print("[Aurora Debug] Git command failed:", str(e))
        return {"status": "error", "message": f"Git command failed: {e}"}
    except Exception as e:
        print("[Aurora Debug] Exception:", str(e))
        return {"status": "error", "message": str(e)}


# ✅ Aurora memory用に共用エイリアスを定義
push_memory_to_github = push_whiteboard_to_github
