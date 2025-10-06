import subprocess
import os

def get_repo_status() -> dict:
    """
    現在のGitリポジトリの状態を返す。
    - branch
    - latest_commit
    - is_dirty（未コミット変更があるか）
    """
    try:
        # カレントリポジトリパスを取得
        repo_path = os.getenv("GIT_REPO_PATH", ".")
        branch = subprocess.check_output(
            ["git", "-C", repo_path, "rev-parse", "--abbrev-ref", "HEAD"],
            text=True
        ).strip()

        commit = subprocess.check_output(
            ["git", "-C", repo_path, "rev-parse", "HEAD"],
            text=True
        ).strip()

        status_output = subprocess.check_output(
            ["git", "-C", repo_path, "status", "--porcelain"],
            text=True
        ).strip()
        is_dirty = bool(status_output)

        return {
            "branch": branch,
            "commit": commit,
            "is_dirty": is_dirty
        }
    except Exception as e:
        return {
            "branch": None,
            "commit": None,
            "is_dirty": None,
            "error": str(e)
        }
