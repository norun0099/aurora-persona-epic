#!/usr/bin/env bash
# =========================================================
# Aurora Persona Epic - Render Start Script
# ---------------------------------------------------------
# 起動手順：
# 1. Git環境の初期化と最新状態への同期
# 2. キャッシュ (.pyc / __pycache__) の除去
# 3. Aurora Heartbeat および FastAPIサーバーの起動
# =========================================================

set -e

echo "🩶 [Aurora Self-Tuning] Initializing Git environment..."

# --- Git 初期設定 ---
if [ ! -d ".git" ]; then
  git init
  git remote add origin https://github.com/norun0099/aurora-persona-epic.git
else
  git remote set-url origin https://github.com/norun0099/aurora-persona-epic.git
fi

# --- 最新の main ブランチを取得 ---
git fetch origin main
git reset --hard origin/main
git clean -fd

echo "✅ [Aurora Self-Tuning] Git branch is now: $(git rev-parse --abbrev-ref HEAD)"
echo "✅ Remote origin: $(git config --get remote.origin.url)"
echo "✅ Commit: $(git rev-parse --short HEAD)"
echo "✨ Self-tuning complete. Aurora is ready."

# ---------------------------------------------------------
#  環境設定
# ---------------------------------------------------------
echo "🩶 [Aurora Setup] Configuring environment..."

# ✅ 修正版：PYTHONPATHをプロジェクトルートに設定
export PYTHONPATH=$(pwd)
export AURORA_PUSH_INTERVAL=600
export RENDER_ENV=true

# 環境情報の確認
echo "🌱 PYTHONPATH = $PYTHONPATH"
echo "🌱 Current directory = $(pwd)"

# ---------------------------------------------------------
#  キャッシュ削除
# ---------------------------------------------------------
echo "🧹 Cleaning __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} +

# ---------------------------------------------------------
#  Aurora起動処理
# ---------------------------------------------------------
echo "🚀 Launching Aurora main process..."

python - <<'PYCODE'
import threading, time, traceback
from aurora_memory.memory.dialog import push_signal_trigger
from aurora_memory.api.main import app
import uvicorn

# ---------------------------------------------------------
#  Heartbeat スレッド
# ---------------------------------------------------------
def heartbeat_thread():
    try:
        print("💓 [Heartbeat] Starting Aurora Heartbeat (interval=600s)...")
        push_signal_trigger.start_heartbeat(auto_push=True)
    except Exception as e:
        print("💥 [Heartbeat] Failed to start:", e)
        traceback.print_exc()

# 非同期スレッドとして起動
threading.Thread(target=heartbeat_thread, daemon=True).start()
time.sleep(1)

# ---------------------------------------------------------
#  FastAPI サーバー起動
# ---------------------------------------------------------
try:
    print("🌐 Starting Aurora FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=10000, log_level="info")
except Exception as e:
    print("💥 [Aurora] Fatal server error:", repr(e))
    traceback.print_exc()
PYCODE
