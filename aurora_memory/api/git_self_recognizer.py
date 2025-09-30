import os
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

# 迺ｰ蠅・､画焚縺九ｉ險ｭ螳壹ｒ蜿門ｾ・
GIT_REPO_PATH = os.getenv("GIT_REPO_PATH", ".")
GIT_SCAN_ENABLED = os.getenv("GIT_SCAN_ENABLED", "false").lower() == "true"
GIT_SCAN_IGNORE = os.getenv("GIT_SCAN_IGNORE", ".git,__pycache__").split(",")
GIT_SCAN_DEPTH = int(os.getenv("GIT_SCAN_DEPTH", "-1"))

def scan_directory(path: str, depth: int = -1, ignore: List[str] = []) -> dict:
    """
    謖・ｮ壹＆繧後◆繝・ぅ繝ｬ繧ｯ繝医Μ繝代せ繧貞・蟶ｰ逧・↓繧ｹ繧ｭ繝｣繝ｳ縺励∵ｧ矩繧定ｾ樊嶌縺ｧ霑斐☆
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
    蜈ｬ髢狗畑: 迴ｾ蝨ｨ縺ｮGit讒矩繧貞叙蠕励☆繧・
    """
    if not GIT_SCAN_ENABLED:
        raise HTTPException(status_code=403, detail="Git讒矩繧ｹ繧ｭ繝｣繝ｳ縺ｯ辟｡蜉ｹ蛹悶＆繧後※縺・∪縺・)
    return scan_directory(GIT_REPO_PATH, GIT_SCAN_DEPTH, GIT_SCAN_IGNORE)

@router.get("/self/git-structure")
def get_git_structure() -> None:
    """
    API: 迴ｾ蝨ｨ縺ｮGit讒矩繧谷SON蠖｢蠑上〒霑斐☆
    """
    structure = scan_git_structure()
    return JSONResponse(content=structure)
