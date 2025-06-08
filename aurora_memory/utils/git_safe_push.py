#!/usr/bin/env python3
import subprocess
import sys


def run(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def safe_push(remote: str = "origin", branch: str = "main") -> bool:
    fetch = run(["git", "fetch", remote, branch])
    print(fetch.stdout)
    if fetch.returncode != 0:
        return False

try:
        local_head = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        remote_head = subprocess.check_output(
            ["git", "rev-parse", f"{remote}/{branch}"]
        ).decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"rev-parse failed: {e}")
        return False

    if local_head != remote_head:
        print(f"Remote {remote}/{branch} has new commits. Attempting rebase...")
        rebase = run(["git", "pull", "--rebase", remote, branch])
        print(rebase.stdout)
        if rebase.returncode != 0:
            print("Rebase failed")
            return False

    push = run(["git", "push", remote, branch])
    print(push.stdout)
    if push.returncode != 0:
        print("Push failed")
        return False
    return True


def main():
    remote = sys.argv[1] if len(sys.argv) > 1 else "origin"
    branch = sys.argv[2] if len(sys.argv) > 2 else "main"
    success = safe_push(remote, branch)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
