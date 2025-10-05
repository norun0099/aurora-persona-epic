from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from aurora_memory.utils import git_file_editor, self_edit_guard
from typing import Any, Dict, TypeVar, Callable, Coroutine, cast

router = APIRouter()

T = TypeVar("T")


class UpdateRepoFileRequest(BaseModel):
    filepath: str
    content: str
    author: str
    reason: str


class UpdateRepoFileResponse(BaseModel):
    status: str
    message: str


def typed_post(
    path: str, response_model: type[BaseModel]
) -> Callable[
    [Callable[..., Coroutine[Any, Any, Dict[str, str]]]],
    Callable[..., Coroutine[Any, Any, Dict[str, str]]]
]:
    """Wrapper to ensure FastAPI post decorator is recognized as typed."""
    return cast(
        Callable[
            [Callable[..., Coroutine[Any, Any, Dict[str, str]]]],
            Callable[..., Coroutine[Any, Any, Dict[str, str]]],
        ],
        router.post(path, response_model=response_model),
    )


@typed_post("/update-repo-file", response_model=UpdateRepoFileResponse)
async def update_repo_file(request: UpdateRepoFileRequest) -> Dict[str, str]:
    """Update a repository file, validate content, commit, and push changes."""

    filepath: str = request.filepath
    content: str = request.content
    author: str = request.author
    reason: str = request.reason

    try:
        self_edit_guard.validate_file_content(filepath, content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")

    try:
        git_file_editor.write_file(filepath, content)
        git_file_editor.commit_and_push(filepath, author, reason)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git operation failed: {str(e)}")

    return {"status": "success", "message": f"File {filepath} updated and pushed by {author}"}
