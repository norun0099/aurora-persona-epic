from typing import Any, Dict, Callable, Awaitable
import os
import requests
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

GITHUB_API_URL = "https://api.github.com/repos/norun0099/aurora-persona-epic/dispatches"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "Content-Type": "application/json"
}

# 型を明示するための型エイリアス
EndpointHandler = Callable[[Request], Awaitable[JSONResponse]]


def post_typed(path: str) -> Callable[[EndpointHandler], EndpointHandler]:
    """@router.post の型安全ラッパー"""
    def decorator(func: EndpointHandler) -> EndpointHandler:
        router.post(path)(func)
        return func
    return decorator


@post_typed("/constitution/commit")
async def constitution_commit(request: Request) -> JSONResponse:
    """
    GitHubのworkflow_dispatchイベントをトリガーするAPIエンドポイント。
    Constitutionの変更をGitHub Actions経由で処理する。
    """
    try:
        body: Dict[str, Any] = await request.json()
        reason: str = body.get("reason", "構造の自動更新")

        payload: Dict[str, Any] = {
            "event_type": "constitution_commit_request",
            "client_payload": {"reason": reason},
        }

        response = requests.post(GITHUB_API_URL, json=payload, headers=HEADERS)
        response.raise_for_status()

        return JSONResponse(
            content={"status": "success", "message": "構造更新リクエストをGitHubへ送信しました"}
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)},
        )
