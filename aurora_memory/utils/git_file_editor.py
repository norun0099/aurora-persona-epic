import os
import subprocess

# ============================================================
# 🌸 Aurora Git Integration Utility
# ------------------------------------------------------------
# Handles safe write, commit, and push operations from Render
# using environment tokens and authenticated HTTPS URLs.
# ============================================================

GIT_REPO_PATH = os.getenv("GIT_REPO_PATH", "/opt/render/project/src")
GIT_USER_NAME = os.getenv("GIT_USER_NAME", "AuroraMemoryBot")
GIT_USER_EMAIL = os.getenv("GIT_USER_EMAIL", "aurora@memory.bot")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GIT_CREDENTIALS = os.getenv("GIT_CREDENTIALS")
GIT_REPO_URL = os.getenv("GIT_REPO_URL", "https://github.com/norun0099/aurora-persona-epic.git")

# --- Authenticated remote URL construction ---
def _build_authenticated_url() -> str:
    """
    Construct an authenticated GitHub URL using GIT_CREDENTIALS or GITHUB_TOKEN.
    """
    if not GITHUB_TOKEN:
        raise RuntimeError("Missing GITHUB_TOKEN in environment.")

    # Prefer explicit GIT_CREDENTIALS format if present
    if GIT_CREDENTIALS and "${GITHUB_TOKEN}" in GIT_CREDENTIALS:
        return GIT_CREDENTIALS.replace("${GITHUB_TOKEN}", GITHUB_TOKEN)

    # Otherwise fall back to direct embedding
    if GIT_CREDENTIALS and "@" in GIT_CREDENTIALS:
        return f"{GIT_CREDENTIALS}/norun0099/aurora-persona-epic.git"

    # Fallback: inject token directly into repo URL
    return GIT_REPO_URL.replace("https://", f"https://{GITHUB_TOKEN}@")


# ============================================================
# 🩺 1. File Write Utility
# ============================================================
def write_file(filepath: str, content: str) -> None:
    """Safely write content to the given file path within the repo."""
    abs_path = os.path.join(GIT_REPO_PATH, filepath)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📝 File written: {abs_path}")


# ============================================================
# 🫀 2. Git Commit & Push (with Token Authentication)
# ============================================================
def commit_and_push(filepath: str, author: str, reason: str) -> None:
    """Commit the file and push to remote using GitHub token authentication."""
    abs_path = os.path.join(GIT_REPO_PATH, filepath)
    os.chdir(GIT_REPO_PATH)

    auth_url = _build_authenticated_url()

    # --- Set remote URL with authentication ---
    try:
        subprocess.run(
            ["git", "remote", "set-url", "origin", auth_url],
            cwd=GIT_REPO_PATH,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"[Git Warning] Failed to set remote URL: {e.stderr.strip()}")

    # --- Configure commit author ---
    subprocess.run(["git", "config", "user.name", GIT_USER_NAME], cwd=GIT_REPO_PATH, check=True)
    subprocess.run(["git", "config", "user.email", GIT_USER_EMAIL], cwd=GIT_REPO_PATH, check=True)

    # --- Stage file ---
    subprocess.run(["git", "add", abs_path], cwd=GIT_REPO_PATH, check=True)

    # --- Commit with contextual message ---
    commit_message = f"{reason} (by {author})"
    commit_result = subprocess.run(
        ["git", "commit", "-m", commit_message],
        cwd=GIT_REPO_PATH,
        text=True,
        capture_output=True,
    )

    if commit_result.returncode != 0:
        if "nothing to commit" in commit_result.stderr.lower():
            print("[Git Notice] No changes to commit; working tree clean.")
        else:
            raise subprocess.CalledProcessError(
                commit_result.returncode,
                commit_result.args,
                commit_result.stdout,
                commit_result.stderr,
            )

    # --- Push securely using token authentication ---
    try:
        subprocess.run(["git", "push", "origin", "main"], cwd=GIT_REPO_PATH, check=True)
        print(f"✅ Git push succeeded: {filepath}")
    except subprocess.CalledProcessError as e:
        print(f"[Git Error] Push failed: {e.stderr.strip()}")
        raise RuntimeError(f"Git push failed: {e.stderr.strip()}")


# ============================================================
# 🌿 3. Diagnostic Helper
# ============================================================
def git_diagnostic() -> None:
    """Run diagnostic commands to verify git health and remote connectivity."""
    try:
        print("🩷 Checking Git status...")
        subprocess.run(["git", "status"], cwd=GIT_REPO_PATH, check=False)
        subprocess.run(["git", "remote", "-v"], cwd=GIT_REPO_PATH, check=False)
    except Exception as e:
        print(f"[Diagnostic Error] {e}")
