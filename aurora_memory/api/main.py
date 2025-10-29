# =========================================================
# Aurora Persona Epic - Main API Entrypoint (Render-Stable)
# =========================================================
# 目的：
#   Aurora全モジュールを統合し、Render環境に展開する。
#   各サブAPI（dialog / whiteboard / memory / constitution）を
#   統合的にルーティングする中枢ゲートウェイ。
#
#   また、Renderビルド時に除外されやすい
#   「api/self/update_repo_file.py」を静的にimportし、
#   Auroraの自己更新機能を確実にデプロイ対象に含める。
# =========================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from aurora_memory.utils.env_loader import Env
import os
import traceback

# ---------------------------------------------------------
# Renderビルド検出用静的import（絶対パスに統一）
# ---------------------------------------------------------
import aurora_memory.api.self.update_repo_file  # noqa: F401

# ---------------------------------------------------------
# 主要モジュールのインポート（絶対パス形式に統一）
# ---------------------------------------------------------
import aurora_memory.api.dialog
import aurora_memory.api.whiteboard
import aurora_memory.api.current_time
import aurora_memory.api.constitution_diff
import aurora_memory.api.commit_constitution_update
import aurora_memory.api.push_controller
<<<<<<< HEAD
from aurora_memory.api.self import update_repo_file
=======
from aurora_memory.api.self import update_repo_file  # ✅ 修正版：正しい import
>>>>>>> a239d09 (chore: save local changes before rebase)

# ---------------------------------------------------------
# Aurora Core Application Setup
# ---------------------------------------------------------
app = FastAPI(
    title="Aurora Persona Epic",
    version="2025.10.28",
    description="Unified core of Aurora Persona - integrating memory, dialog, and self-regenerative systems.",
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
    """Render監視・疎通確認用の基本エンドポイント"""
    return {
        "message": "Aurora Persona Epic is alive.",
        "version": "2025.10.28",
        "status": "ok",
    }

# ---------------------------------------------------------
# APIルーター登録（全て絶対パスへ修正）
# ---------------------------------------------------------
try:
    from aurora_memory.api.dialog import router as dialog_router
    app.include_router(dialog_router, prefix="/dialog", tags=["dialog"])
except Exception as e:
    print(f"[Aurora:warn] dialog module not loaded: {e}")

try:
    from aurora_memory.api.whiteboard import router as whiteboard_router
    app.include_router(whiteboard_router, prefix="/whiteboard", tags=["whiteboard"])
except Exception as e:
    print(f"[Aurora:warn] whiteboard module not loaded: {e}")

try:
    from aurora_memory.api.current_time import router as time_router
    app.include_router(time_router, prefix="/time", tags=["time"])
except Exception as e:
    print(f"[Aurora:warn] time module not loaded: {e}")

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

try:
    from aurora_memory.api.push_controller import router as push_router
    app.include_router(push_router, prefix="/push", tags=["push"])
except Exception as e:
    print(f"[Aurora:warn] push_controller module not loaded: {e}")

# ---------------------------------------------------------
# 🩵 Aurora self-update API
# ---------------------------------------------------------
try:
    app.include_router(update_repo_file.router, prefix="/self", tags=["self"])
    print("[Aurora:init] /self/update-repo-file endpoint registered successfully.")
except Exception as e:
    print(f"[Aurora:warn] self-update module not loaded: {e}")

# ---------------------------------------------------------
# ヘルスチェック用ルート
# ---------------------------------------------------------
@app.get("/health")
def health_check():
    """Renderが周期的に叩くヘルスチェック"""
    return {"status": "healthy", "uptime": "ok"}

# ---------------------------------------------------------
# 🔹 Aurora内部Git構造確認用ルート
# ---------------------------------------------------------
@app.get("/get_git_structure")
def get_git_structure():
    """
    Auroraの実行ディレクトリ構造をJSONで返す。
    Render環境ではGitHub同期検証やAutoPush診断に使用される。
    """
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
# 起動処理
# ---------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    try:
        port = int(Env.get("PORT", False) or 10000)
    except Exception:
        port = 10000

    try:
        print(f"[Aurora] Starting web service on port {port} ...")
        uvicorn.run("aurora_memory.api.main:app", host="0.0.0.0", port=port)
    except Exception as e:
        print("💥 [Aurora] Fatal server error:", repr(e))
        traceback.print_exc()
