"""
Aurora self API package.
Connects internal bridge modules and exposes FastAPI routers for Render integrations.
"""

from fastapi import APIRouter
from aurora_memory.api.self import update_repo_file

# Initialize FastAPI router and include submodules
router = APIRouter()

# ✅ Ensure the update_repo_file router is included
router.include_router(update_repo_file.router)

# Export router and submodules
__all__ = ["router", "update_repo_file"]
