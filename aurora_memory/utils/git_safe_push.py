#!/usr/bin/env python3
import subprocess
import sys


def run(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def safe_push(remote="origin", branch="main"):
    fetch = run(["git", "fetch", remote, branch])
    print(fetch.stdout)
    if fetch.returncode != 0:
        return False

    local_head = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    remote_head = subprocess.check_output(["git", "rev-parse", f"{remote}/{branch}"]).decode().strip()

    if local_head != remote_head:
        print(f"Remote {remote}/{branch} has new commits. Skipping push.")
        return False

    push = run(["git", "push", remote, branch])
    print(push.stdout)
    if push.returncode != 0:
        print("Push failed")
        return False
    return True


def main():
    success = safe_push()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
