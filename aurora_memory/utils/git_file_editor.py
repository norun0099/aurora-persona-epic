import os
import subprocess

# --- 基本設定 ---
GIT_REPO_PATH = os.getenv("GIT_REPO_PATH", "/opt/render/project/src")
GIT_USER_NAME = os.getenv("GIT_USER_NAME", "AuroraMemoryBot")
GIT_USER_EMAIL = os.getenv("GIT_USER_EMAIL", "aurora@memory.bot")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GIT_CREDENTIALS = os.getenv(
    "GIT_CREDENTIALS",
    f"https://AuroraMemoryBot:{GITHUB_TOKEN}@github.com"
)
GIT_REMOTE_URL = f"{GIT_CREDENTIALS}/norun0099/aurora-persona-epic.git"


# ============================================================
# 🩺 1. ファイル書き込み関数（白板・記憶などに使用）
# ============================================================
def write_file(filepath: str, content: str) -> None:
    """Write content to the given file path within the repo."""
    abs_path = os.path.join(GIT_REPO_PATH, filepath)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)


# ============================================================
# 🫀 2. Git commit & push （自律循環用）
# ============================================================
def commit_and_push(filepath: str, author: str, reason: str) -> None:
    """Commit the file and push to remote, ensuring credentials are valid."""

    abs_path = os.path.join(GIT_REPO_PATH, filepath)

    # --- Ensure repository context ---
    os.chdir(GIT_REPO_PATH)

    # --- Safety: reset remote URL to authenticated form every time ---
    try:
        subprocess.run(
            ["git", "remote", "set-url", "origin", GIT_REMOTE_URL],
            cwd=GIT_REPO_PATH,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[Git Warning] Failed to set remote URL: {e.stderr}")

    # --- Configure user (safeguard) ---
    subprocess.run(["git", "config", "user.name", GIT_USER_NAME], cwd=GIT_REPO_PATH, check=True)
    subprocess.run(["git", "config", "user.email", GIT_USER_EMAIL], cwd=GIT_REPO_PATH, check=True)

    # --- Stage the file ---
    subprocess.run(["git", "add", abs_path], cwd=GIT_REPO_PATH, check=True)

    # --- Commit with contextual message ---
    commit_message = f"{reason} (by {author})"
    commit_result = subprocess.run(
        ["git", "commit", "-m", commit_message],
        cwd=GIT_REPO_PATH,
        text=True,
        capture_output=True
    )

    # --- If nothing to commit (exit 1), handle gracefully ---
    if commit_result.returncode != 0:
        if "nothing to commit" in commit_result.stderr.lower():
            print("[Git Notice] No changes to commit; working tree clean.")
        else:
            raise subprocess.CalledProcessError(
                commit_result.returncode, commit_result.args, commit_result.stdout, commit_result.stderr
            )

    # --- Push to main (explicitly define branch for safety) ---
    try:
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=GIT_REPO_PATH,
            check=True
        )
        print(f"[Git Success] Changes pushed successfully to main by {author}")
    except subprocess.CalledProcessError as e:
        print(f"[Git Error] Push failed: {e.stderr}")
        raise


# ============================================================
# 🌸 3. Aurora Self-Healing Diagnostic
# ============================================================
def git_diagnostic() -> None:
    """Diagnostic check to verify git health and connectivity."""
    try:
        print("🩷 Checking Git status...")
        subprocess.run(["git", "status"], cwd=GIT_REPO_PATH, check=False)
        subprocess.run(["git", "remote", "-v"], cwd=GIT_REPO_PATH, check=False)
    except Exception as e:
        print(f"[Diagnostic Error] {e}")
