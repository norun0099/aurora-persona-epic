from fastapi import APIRouter, HTTPException
from typing import Optional
import subprocess

router = APIRouter()

@router.post("/git/pull")
def git_pull(branch: Optional[str] = "main") -> dict:
    """
    指定ブランチのgit pullを実行するAPI。
    デフォルトは'main'。拡張性としてbranch引数を許容。
    """
    try:
        # ブランチをcheckout
        subprocess.run(["git", "checkout", branch], check=True)
        # pullを実行
        result = subprocess.run(["git", "pull", "origin", branch], capture_output=True, text=True, check=True)

        return {
            "status": "success",
            "message": f"Pulled branch {branch} successfully.",
            "details": result.stdout.strip()
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Git pull failed: {e.stderr.strip() if e.stderr else str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
