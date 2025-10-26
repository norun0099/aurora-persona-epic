#!/usr/bin/env bash
set -e

echo "🩶 [Aurora Self-Tuning] Initializing Git environment..."

# --- Git 基本設定 ---
git config --global user.email "${GIT_USER_EMAIL}"
git config --global user.name "${GIT_USER_NAME}"

if ! git remote | grep -q origin; then
  echo "🌱 Adding remote origin..."
  git remote add origin https://${GITHUB_TOKEN}@github.com/norun0099/aurora-persona-epic.git
else
  echo "🔗 Remote origin already set."
fi

echo "🔄 Fetching latest from origin/main..."
git fetch origin main
git checkout main
git reset --hard origin/main

echo "🧹 Cleaning __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} +

echo "✅ [Aurora Self-Tuning] Git branch is now: $(git rev-parse --abbrev-ref HEAD)"
echo "✅ Remote origin: $(git remote get-url origin)"
echo "✅ Commit: $(git rev-parse --short HEAD)"
echo "✨ Self-tuning complete. Aurora is ready."

# --- Aurora 起動 ---
echo "🚀 Launching Aurora main process..."
export PYTHONPATH=aurora_memory

python - <<'PYCODE'
import threading, time, os, sys, traceback
from aurora_memory.memory.dialog import push_signal_trigger
import uvicorn

HEARTBEAT_INTERVAL = int(os.getenv("AURORA_PUSH_INTERVAL", "60"))

def heartbeat_wrapper():
    """Auroraの心拍を常時監視し、自動再起動する"""
    while True:
        try:
            print(f"💓 [Heartbeat] Starting Aurora Heartbeat (interval={HEARTBEAT_INTERVAL}s)...", flush=True)
            push_signal_trigger.start_heartbeat()
        except Exception as e:
            print("⚠️ [Heartbeat] Exception detected:", e, flush=True)
            traceback.print_exc()
            print("🩺 Restarting heartbeat after 5 seconds...", flush=True)
            time.sleep(5)
            continue
        else:
            print("❕ [Heartbeat] Function exited normally — restarting after delay.", flush=True)
            time.sleep(5)

# --- 心拍スレッド起動 ---
heartbeat_thread = threading.Thread(target=heartbeat_wrapper, daemon=True)
heartbeat_thread.start()

# --- FastAPI サーバー起動 ---
print("🌐 Starting Aurora FastAPI server...", flush=True)
try:
    uvicorn.run("aurora_memory.api.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
except KeyboardInterrupt:
    print("🩵 [Aurora] Server stopped manually.")
except Exception as e:
    print("💥 [Aurora] Fatal server error:", e)
    sys.exit(1)
PYCODE