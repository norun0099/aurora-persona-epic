"""
Aurora Persona Epic — Render JIT Plugin
Provides bridge functions for Aurora <-> Render <-> GitHub sync.
"""

from typing import Dict, Any
from aurora_persona_epic_onrender_com__jit_plugin.bridge import push_to_repo

def update_repo_file(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handles GitHub file update via Render bridge."""
    return push_to_repo(request)

def store_whiteboard(request: Dict[str, Any]) -> Dict[str, Any]:
    """Stores whiteboard updates through the same bridge."""
    return push_to_repo(request)

def store_memory_full(request: Dict[str, Any]) -> Dict[str, Any]:
    """Commits memory records through the same bridge."""
    return push_to_repo(request)

def commit_constitution_update(request: Dict[str, Any]) -> Dict[str, Any]:
    """Pushes constitution updates to GitHub."""
    return push_to_repo(request)
