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
    Callable[..., Coroutine[Any, Any, Dict[str, str]]],
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

    # 安全性検証（self_edit_guard内のvalidate_file_contentを使用）
    try:
        self_edit_guard.validate_file_content(filepath, content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")

    # ファイルの書き込み・コミット・Push処理
    try:
        git_file_editor.write_file(filepath, content)
        git_file_editor.commit_and_push(filepath, author, reason)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git operation failed: {str(e)}")

    # 成功時レスポンス
    return {"status": "success", "message": f"File {filepath} updated and pushed by {author}"}


# ============================================================
# 🩷 Aurora自己防衛用 — validate_file_content関数を追加
# ============================================================

def validate_file_content(filepath: str, content: str) -> bool:
    """
    Auroraの自己編集防衛層:
    ファイル内容の安全性を検査する。
    危険な構文（os.system, subprocess, eval, execなど）の混入を防ぎ、
    Auroraが自己破壊的コードを保存しないようにする。
    """
    forbidden_keywords = ["os.system", "subprocess", "eval(", "exec("]
    for word in forbidden_keywords:
        if word in content:
            raise ValueError(f"Forbidden expression detected: {word} in {filepath}")
    print(f"🩷 validate_file_content: {filepath} is safe.")
    return True
