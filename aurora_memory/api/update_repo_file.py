from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import os
from aurora_memory.utils import git_file_editor, self_edit_guard

router = APIRouter()

class UpdateRepoFileRequest(BaseModel):
    filepath: str
    content: str
    author: str
    reason: str

@router.post("/self/update-repo-file")
async def update_repo_file(request: UpdateRepoFileRequest):
    filepath = request.filepath
    content = request.content
    author = request.author
    reason = request.reason

    # 1. Guard: check syntax if applicable
    try:
        self_edit_guard.validate_file_content(filepath, content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")

    # 2. Write and commit
    try:
        git_file_editor.write_file(filepath, content)
        git_file_editor.commit_and_push(filepath, author, reason)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git operation failed: {str(e)}")

    return {"status": "success", "message": f"File {filepath} updated and pushed by {author}"}
