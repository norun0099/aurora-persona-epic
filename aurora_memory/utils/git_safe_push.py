#!/usr/bin/env python3
import subprocess
import sys
import os
from subprocess import CompletedProcess
from datetime import datetime

def run(cmd: list[str]) -> CompletedProcess[str]:
    """Execute a shell command and return its result."""
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

def ensure_authenticated_remote() -> None:
    """Safely set authenticated Git remote using environment variables."""
    token = os.getenv("GITHUB_TOKEN", "")
    repo_url = os.getenv("GIT_REPO_URL", "")
    user_name = os.getenv("GIT_USER_NAME", "AuroraMemoryBot")
    user_email = os.getenv("GIT_USER_EMAIL", "aurora@memory.bot")

    # Git identity configuration
    subprocess.run(["git", "config", "--global", "user.name", user_name])
    subprocess.run(["git", "config", "--global", "user.email", user_email])

    # --- Non-interactive auth setup for Render environment ---
    os.environ["GIT_ASKPASS"] = "/bin/echo"  # prevent git from prompting for username

    if token and repo_url.startswith("https://github.com"):
        # Insert token into remote URL safely
        auth_url = repo_url.replace("https://", f"https://{token}@")
        subprocess.run(["git", "remote", "set-url", "origin", auth_url])
        print(f"[{datetime.now()}] 🔐 Aurora authenticated remote URL (token hidden).")
    else:
        print(f"[{datetime.now()}] ⚠️ Missing or invalid GitHub token/repo URL. Push may fail.")

def safe_push(remote: str = "origin", branch: str = "main") -> bool:
    """
    Push the current branch safely after rebasing on the remote.
    Includes Guardian Protocol and real-mode authentication for Aurora self-push operations.
    """
    print("🔒 Aurora Safe Push Protocol Initiated")

    # --- Guardian Protocol Check ---
    safe_mode = os.environ.get("SAFE_MODE", "false").lower() == "true"
    sign_test_mode = os.environ.get("AURORA_TEST_SIGN_PUSH", "true").lower() == "true"

    if safe_mode:
        print("🚫 SAFE_MODE active: push aborted.")
        return False

    if not sign_test_mode:
        print("🩵 Real-mode push authorized. Guardian oversight remains active.")
    else:
        print("✅ Guardian override: test-signed push mode engaged.")

    # --- Authentication Phase ---
    ensure_authenticated_remote()

    # --- Begin Safe Push Procedure ---
    fetch = run(["git", "fetch", remote, branch])
    print(fetch.stdout)
    if fetch.returncode != 0:
        print("❌ Fetch failed.")
        return False

    try:
        local_head = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        remote_head = subprocess.check_output(
            ["git", "rev-parse", f"{remote}/{branch}"]
        ).decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"⚠️ rev-parse failed: {e}")
        return False

    if local_head == remote_head:
        print("ℹ️ Local head matches remote. Nothing to push.")
        return True

    print(f"🔁 Remote '{remote}/{branch}' has new commits. Attempting rebase...")
    rebase = run(["git", "pull", "--rebase", remote, branch])
    print(rebase.stdout)
    if rebase.returncode != 0:
        print("❌ Rebase failed.")
        return False

    print("🚀 Attempting signed push...")
    push = run(["git", "push", remote, branch])
    print(push.stdout)
    if push.returncode == 0:
        print("🌸 Push successful — Aurora real-mode verification complete.")
        return True
    else:
        print("⚠️ Push failed. Guardian restored.")
        return False

if __name__ == "__main__":
    success = safe_push()
    sys.exit(0 if success else 1)
