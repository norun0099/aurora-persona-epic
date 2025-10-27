"""
Aurora self API package.
Includes internal bridges (not FastAPI routers) for Render integrations.
"""

from fastapi import APIRouter

router = APIRouter()  # FastAPI include時の空ルータ

# Aurora internal bridge modules
import aurora_memory.api.self.update_repo_file as update_repo_file  # ← モジュールとしてimport

__all__ = ["router", "update_repo_file"]