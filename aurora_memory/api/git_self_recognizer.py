import os
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

# 環墁E��数から設定を取征E
GIT_REPO_PATH = os.getenv("GIT_REPO_PATH", ".")
GIT_SCAN_ENABLED = os.getenv("GIT_SCAN_ENABLED", "false").lower() == "true"
GIT_SCAN_IGNORE = os.getenv("GIT_SCAN_IGNORE", ".git,__pycache__").split(",")
GIT_SCAN_DEPTH = int(os.getenv("GIT_SCAN_DEPTH", "-1"))

def scan_directory(path: str, depth: int = -1, ignore: List[str] = []) -> dict:
    """
    持E��されたチE��レクトリパスを�E帰皁E��スキャンし、構造を辞書で返す
    """
    result = {}
    try:
        entries = os.listdir(path)
    except Exception as e:
        return {"error": str(e)}

    for entry in entries:
        full_path = os.path.join(path, entry)
        rel_path = os.path.relpath(full_path, GIT_REPO_PATH)

        if any(part in rel_path.split(os.sep) for part in ignore):
            continue

        if os.path.isdir(full_path):
            if depth == 0:
                result[entry] = "<dir>"
            else:
                result[entry] = scan_directory(
                    full_path, depth - 1 if depth > 0 else -1, ignore
                )
        else:
            result[entry] = "<file>"

    return result

def scan_git_structure() -> dict:
    """
    公開用: 現在のGit構造を取得すめE
    """
    if not GIT_SCAN_ENABLED:
        raise HTTPException(status_code=403, detail="Git構造スキャンは無効化されてぁE��ぁE)
    return scan_directory(GIT_REPO_PATH, GIT_SCAN_DEPTH, GIT_SCAN_IGNORE)

@router.get("/self/git-structure")
def get_git_structure() -> None:
    """
    API: 現在のGit構造をJSON形式で返す
    """
    structure = scan_git_structure()
    return JSONResponse(content=structure)
