"""
Aurora self API package.
Includes internal bridges (not FastAPI routers) for Render integrations.
"""

from fastapi import APIRouter

router = APIRouter()  # 空routerを定義して、FastAPI include時のエラーを防ぐ

# Aurora self-layer internal modules
from .update_repo_file import update_repo_file  # noqa: F401

__all__ = ["router", "update_repo_file"]