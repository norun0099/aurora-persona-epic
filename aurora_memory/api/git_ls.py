from fastapi import APIRouter, HTTPException
import subprocess
from typing import List

router = APIRouter()

@router.get("/git/ls")
def git_ls() -> List[str]:
    """
    コミット済みの全ファイル一覧を取得するAPI。
    HEAD（最新コミット）のファイルツリーを再帰的に表示する。
    """
    try:
        # git ls-tree を実行
        result = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "HEAD"],
            capture_output=True, text=True, check=True
        )

        # 出力を1行ごとのリストに整形
        file_list = result.stdout.strip().split("\n") if result.stdout else []
        return file_list
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Git ls-tree failed: {e.stderr.strip() if e.stderr else str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
