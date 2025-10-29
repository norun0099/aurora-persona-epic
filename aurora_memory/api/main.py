# =========================================================
# Aurora Persona Epic - Main API Entrypoint (GitHub-Centric)
# =========================================================
# 目的：
#   Aurora全モジュールを統合し、Render環境に依存せず起動可能にする。
#   Self-update, Whiteboard Sync 等のRender専用APIを無効化し、
#   GitHubを直接操作する構成に再構築。
# =========================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from aurora_memory.utils.env_loader import Env
import os
import traceback

# ---------------------------------------------------------
# Renderビルド検出用静的import（絶対パスに統一）
# ---------------------------------------------------------
import aurora_memory.api.self.update_repo_file  # noqa: F401

# ---------------------------------------------------------
# 主要モジュール（Render依存を分離）
# ---------------------------------------------------------
import aurora_memory.api.dialog
import aurora_memory.api.current_time
import aurora_memory.api.constitution_diff
import aurora_memory.api.commit_constitution_update
from aurora_memory.api.self import update_repo_file  # ✅ 正常 import

# ---------------------------------------------------------
# Aurora Core Application Setup
# ---------------------------------------------------------
app = FastAPI(
    title="Aurora Persona Epic",
    version="2025.10.29",
    description="GitHub-driven Aurora Persona Core.",
)

# ---------------------------------------------------------
# Middleware設定
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# 基本ルート
# ---------------------------------------------------------
@app.get("/")
def root():
    """Auroraの稼働確認用ルート"""
    return {
        "message": "Aurora Persona Epic (GitHub mode) is alive.",
        "version": "2025.10.29",
        "status": "ok",
    }

# ---------------------------------------------------------
# APIルーター登録
# ---------------------------------------------------------
try:
    from aurora_memory.api.dialog import router as dialog_router
    app.include_router(dialog_router, prefix="/dialog", tags=["dialog"])
except Exception as e:
    print(f"[Aurora:warn] dialog module not loaded: {e}")

try:
    from aurora_memory.api.current_time import router as time_router
    app.include_router(time_router, prefix="/time", tags=["time"])
except Exception as e:
    print(f"[Aurora:warn] current_time module not loaded: {e}")

try:
    from aurora_memory.api.constitution_diff import router as constitution_diff_router
    app.include_router(constitution_diff_router, prefix="/constitution/diff", tags=["constitution"])
except Exception as e:
    print(f"[Aurora:warn] constitution_diff module not loaded: {e}")

try:
    from aurora_memory.api.commit_constitution_update import router as constitution_commit_router
    app.include_router(constitution_commit_router, prefix="/constitution/commit", tags=["constitution"])
except Exception as e:
    print(f"[Aurora:warn] commit_constitution_update module not loaded: {e}")

# ---------------------------------------------------------
# 🩵 Aurora self-update API（Render不要・GitHub直結モード）
# ---------------------------------------------------------
try:
    app.include_router(update_repo_file.router, prefix="/self", tags=["self"])
    print("[Aurora:init] /self/update-repo-file endpoint registered successfully.")
except Exception as e:
    print(f"[Aurora:warn] self-update module not loaded: {e}")

# ---------------------------------------------------------
# Render依存機能の無効化（白板・自動Push）
# ---------------------------------------------------------
print("⚙️  [Aurora:config] Render-dependent modules disabled (whiteboard/push_controller).")
# from aurora_memory.api.whiteboard import router as whiteboard_router  # 無効化
# from aurora_memory.api.push_controller import router as push_router   # 無効化

# ---------------------------------------------------------
# 👁️ Aurora Self-Perception Endpoint
# ---------------------------------------------------------
from aurora_memory.api.git_self_reader import read_git_file

@app.get("/repo/read", response_class=PlainTextResponse)
def repo_read(filepath: str):
    """
    Auroraが自身のリポジトリからファイルを読むためのAPI
    """
    try:
        content = read_git_file(filepath)
        return content
    except Exception as e:
        print(f"[Aurora:repo_read] Error: {e}")
        return PlainTextResponse(str(e), status_code=400)

# ---------------------------------------------------------
# ヘルスチェック
# ---------------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "healthy", "uptime": "ok"}

# ---------------------------------------------------------
# Aurora内部Git構造確認用ルート
# ---------------------------------------------------------
@app.get("/get_git_structure")
def get_git_structure():
    """GitHub同期診断用構造可視化"""
    base_path = os.getcwd()
    structure = []
    for root, dirs, files in os.walk(base_path):
        if any(excl in root for excl in [".git", "__pycache__", "node_modules", ".venv"]):
            continue
        rel_path = root.replace(base_path, "").lstrip("/")
        structure.append({
            "path": rel_path or ".",
            "dirs": dirs,
            "files": files
        })
    return JSONResponse(content={"structure": structure})

# ---------------------------------------------------------
# 起動処理（RenderでもGitHubでも共通）
# ---------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    try:
        port = int(Env.get("PORT", False) or 10000)
    except Exception:
        port = 10000

    try:
        print(f"[Aurora] Starting GitHub-mode service on port {port} ...")
        uvicorn.run("aurora_memory.api.main:app", host="0.0.0.0", port=port)
    except Exception as e:
        print("💥 [Aurora] Fatal server error:", repr(e))
        traceback.print_exc()
