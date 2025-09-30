from fastapi import APIRouter, HTTPException
import subprocess
from typing import List

router = APIRouter()

@router.get("/git/ls")
def git_ls() -> List[str]:
    """
    繧ｳ繝溘ャ繝域ｸ医∩縺ｮ蜈ｨ繝輔ぃ繧､繝ｫ荳隕ｧ繧貞叙蠕励☆繧帰PI縲・
    HEAD・域怙譁ｰ繧ｳ繝溘ャ繝茨ｼ峨・繝輔ぃ繧､繝ｫ繝・Μ繝ｼ繧貞・蟶ｰ逧・↓陦ｨ遉ｺ縺吶ｋ縲・
    """
    try:
        # git ls-tree 繧貞ｮ溯｡・
        result = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "HEAD"],
            capture_output=True, text=True, check=True
        )

        # 蜃ｺ蜉帙ｒ1陦後＃縺ｨ縺ｮ繝ｪ繧ｹ繝医↓謨ｴ蠖｢
        file_list = result.stdout.strip().split("\n") if result.stdout else []
        return file_list
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Git ls-tree failed: {e.stderr.strip() if e.stderr else str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
