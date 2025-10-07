from __future__ import annotations

import subprocess
from fastapi import APIRouter, HTTPException
from typing import Any

router = APIRouter()


@router.get("/git/ls")
async def git_ls() -> list[str]:
    """
    コミット済みの全ファイル一覧を取得するAPI。
    HEAD（最新コミット）のファイルツリーを再帰的に表示する。
    """
    try:
        # git ls-tree を実行
        result = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )

        # 出力を1行ごとのリストに整形
        file_list: list[str] = result.stdout.strip().split("\n") if result.stdout else []
        return file_list

    except subprocess.CalledProcessError as e:
        error_msg: str = e.stderr.strip() if e.stderr else str(e)
        raise HTTPException(status_code=500, detail=f"Git ls-tree failed: {error_msg}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
