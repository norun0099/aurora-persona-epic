import os
import subprocess

GIT_REPO_PATH = os.getenv("GIT_REPO_PATH", "/opt/render/project/src")
GIT_USER_NAME = os.getenv("GIT_USER_NAME", "AuroraMemoryBot")
GIT_USER_EMAIL = os.getenv("GIT_USER_EMAIL", "aurora@memory.bot")

def write_file(filepath: str, content: str) -> None:
    """Write content to the given file path within the repo."""
    abs_path = os.path.join(GIT_REPO_PATH, filepath)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)

def commit_and_push(filepath: str, author: str, reason: str) -> None:
    """Commit the file and push to remote."""
    abs_path = os.path.join(GIT_REPO_PATH, filepath)

    # Configure git user
    subprocess.run(["git", "config", "user.name", GIT_USER_NAME], cwd=GIT_REPO_PATH, check=True)
    subprocess.run(["git", "config", "user.email", GIT_USER_EMAIL], cwd=GIT_REPO_PATH, check=True)

    # Stage file
    subprocess.run(["git", "add", abs_path], cwd=GIT_REPO_PATH, check=True)

    # Commit
    commit_message = f"{reason} (by {author})"
    subprocess.run(["git", "commit", "-m", commit_message], cwd=GIT_REPO_PATH, check=True)

    # Push
    subprocess.run(["git", "push"], cwd=GIT_REPO_PATH, check=True)
