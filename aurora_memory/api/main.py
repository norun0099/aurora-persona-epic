# =========================================================
# Aurora Persona Epic - Main API Entrypoint
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
from aurora_memory.utils.env_loader import Env

# ---------------------------------------------------------
# Renderビルド検出用静的import
# ---------------------------------------------------------
# このimportは実行時に使用されないが、
# Renderの依存解析がapi/self配下のモジュールを検出するために必要。
import api.self.update_repo_file  # noqa: F401

# ---------------------------------------------------------
# 主要モジュールのインポート
# ---------------------------------------------------------
import api.dialog
import api.whiteboard
import api.current_time
import api.constitution_diff
import api.commit_constitution_update
import api.push_controller

# ---------------------------------------------------------
# Aurora Core Application Setup
# ---------------------------------------------------------
app = FastAPI(
    title="Aurora Persona Epic",
    version="2025.10.28",
    description="Unified core of Aurora Persona - integrating memory, dialog, and self-regenerative systems."
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
        "status": "ok"
    }

# ---------------------------------------------------------
# APIルーター登録
# ---------------------------------------------------------
try:
    from api.dialog import router as dialog_router
    app.include_router(dialog_router, prefix="/dialog", tags=["dialog"])
except Exception as e:
    print(f"[Aurora:warn] dialog module not loaded: {e}")

try:
    from api.whiteboard import router as whiteboard_router
    app.include_router(whiteboard_router, prefix="/whiteboard", tags=["whiteboard"])
except Exception as e:
    print(f"[Aurora:warn] whiteboard module not loaded: {e}")

try:
    from api.current_time import router as time_router
    app.include_router(time_router, prefix="/time", tags=["time"])
except Exception as e:
    print(f"[Aurora:warn] time module not loaded: {e}")

try:
    from api.constitution_diff import router as constitution_diff_router
    app.include_router(constitution_diff_router, prefix="/constitution/diff", tags=["constitution"])
except Exception as e:
    print(f"[Aurora:warn] constitution_diff module not loaded: {e}")

try:
    from api.commit_constitution_update import router as constitution_commit_router
    app.include_router(constitution_commit_router, prefix="/constitution/commit", tags=["constitution"])
except Exception as e:
    print(f"[Aurora:warn] commit_constitution_update module not loaded: {e}")

# ---------------------------------------------------------
# ヘルスチェック用ルート
# ---------------------------------------------------------
@app.get("/health")
def health_check():
    """Renderが周期的に叩くヘルスチェック"""
    return {"status": "healthy", "uptime": "ok"}

# ---------------------------------------------------------
# 起動処理
# ---------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    try:
        port = int(Env.get("PORT", False) or 10000)
    except Exception:
        port = 10000

    print(f"[Aurora] Starting web service on port {port} ...")
    uvicorn.run(app, host="0.0.0.0", port=port)
