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

# ============================================================
# 🔑 Authenticated URL Construction
# ============================================================
def _build_authenticated_url() -> str:
    """
    Construct a correct authenticated GitHub URL using the available credentials.
    Ensures a full path ending with '.git' is returned.
    """
    if not GITHUB_TOKEN:
        raise RuntimeError("Missing GITHUB_TOKEN in environment.")

    # Prefer explicit GIT_CREDENTIALS if available
    if GIT_CREDENTIALS:
        if "${GITHUB_TOKEN}" in GIT_CREDENTIALS:
            base = GIT_CREDENTIALS.replace("${GITHUB_TOKEN}", GITHUB_TOKEN)
        else:
            base = GIT_CREDENTIALS

        # Ensure proper repo suffix
        if base.endswith(".git"):
            return base
        if base.endswith("/"):
            base = base.rstrip("/")
        if "aurora-persona-epic.git" not in base:
            base = f"{base}/norun0099/aurora-persona-epic.git"
        return base

    # Fallback: embed token directly into repo URL
    if GIT_REPO_URL.startswith("https://github.com"):
        return GIT_REPO_URL.replace("https://", f"https://{GIT_USER_NAME}:{GITHUB_TOKEN}@")

    # Final fallback
    return f"https://{GIT_USER_NAME}:{GITHUB_TOKEN}@github.com/norun0099/aurora-persona-epic.git"


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
    print(f"🔐 Authenticated remote URL: {auth_url}")

    # --- Update remote origin ---
    try:
        subprocess.run(
            ["git", "remote", "set-url", "origin", auth_url],
            cwd=GIT_REPO_PATH,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"[Git Warning] Failed to set remote URL: {e.stderr or e.stdout}")

    # --- Configure Git identity ---
    subprocess.run(["git", "config", "user.name", GIT_USER_NAME], cwd=GIT_REPO_PATH, check=True)
    subprocess.run(["git", "config", "user.email", GIT_USER_EMAIL], cwd=GIT_REPO_PATH, check=True)

    # --- Stage and commit changes ---
    subprocess.run(["git", "add", abs_path], cwd=GIT_REPO_PATH, check=True)
    commit_message = f"{reason} (by {author})"

    commit_proc = subprocess.run(
        ["git", "commit", "-m", commit_message],
        cwd=GIT_REPO_PATH,
        text=True,
        capture_output=True,
    )

    if commit_proc.returncode != 0:
        if "nothing to commit" in commit_proc.stderr.lower():
            print("[Git Notice] No changes to commit; working tree clean.")
        else:
            raise RuntimeError(f"Commit failed: {commit_proc.stderr.strip()}")

    # --- Push to remote ---
    try:
        subprocess.run(["git", "push", "origin", "main"], cwd=GIT_REPO_PATH, check=True)
        print(f"✅ Git push succeeded: {filepath}")
    except subprocess.CalledProcessError as e:
        print(f"[Git Error] Push failed: {e.stderr or e.stdout}")
        raise RuntimeError(f"Git push failed: {e.stderr or e.stdout}")


# ============================================================
# 🌿 3. Diagnostic Helper
# ============================================================
def git_diagnostic() -> None:
    """Run diagnostic commands to verify git configuration and remote connectivity."""
    try:
        print("🩷 Checking Git configuration...")
        subprocess.run(["git", "remote", "-v"], cwd=GIT_REPO_PATH, check=False)
        subprocess.run(["git", "status"], cwd=GIT_REPO_PATH, check=False)
    except Exception as e:
        print(f"[Diagnostic Error] {e}")
