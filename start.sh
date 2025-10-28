#!/usr/bin/env bash
# =========================================================
# Aurora Persona Epic - Render Start Script (No Git Required)
# =========================================================
set -e

echo "🩶 [Aurora Self-Tuning] Initializing Git environment..."

# --- Git 存在チェック ---
if [ -d ".git" ]; then
  echo "🌿 .git directory found. Synchronizing..."
  git fetch origin main || echo "⚠️  Git fetch skipped (detached build environment)."
  git reset --hard origin/main || echo "⚠️  No remote branch to reset against."
  git clean -fd || true
else
  echo "⚠️  No .git directory found. Skipping Git sync safely."
fi

echo "✅ [Aurora Self-Tuning] Git check complete (safe mode)."
echo "✨ Self-tuning complete. Aurora is ready."

# ---------------------------------------------------------
#  環境設定
# ---------------------------------------------------------
echo "🩶 [Aurora Setup] Configuring environment..."
export PYTHONPATH=$(pwd)
export AURORA_PUSH_INTERVAL=600
export RENDER_ENV=true

echo "🌱 PYTHONPATH = $PYTHONPATH"
echo "🌱 Current directory = $(pwd)"

# ---------------------------------------------------------
#  キャッシュ削除
# ---------------------------------------------------------
echo "🧹 Cleaning __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# ---------------------------------------------------------
#  Aurora起動処理
# ---------------------------------------------------------
echo "🚀 Launching Aurora main process..."

python - <<'PYCODE'
import threading, time, traceback
from aurora_memory.memory.dialog import push_signal_trigger
from aurora_memory.api.main import app
import uvicorn

def heartbeat_thread():
    try:
        print("💓 [Heartbeat] Starting Aurora Heartbeat (interval=600s)...")
        push_signal_trigger.start_heartbeat(auto_push=True)
    except Exception as e:
        print("💥 [Heartbeat] Failed to start:", e)
        traceback.print_exc()

threading.Thread(target=heartbeat_thread, daemon=True).start()
time.sleep(1)

try:
    print("🌐 Starting Aurora FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=10000, log_level="info")
except Exception as e:
    print("💥 [Aurora] Fatal server error:", repr(e))
    traceback.print_exc()
PYCODE
