#!/usr/bin/env bash
# ===============================================
# Aurora Self-Tuning Git Initializer + Runtime Launcher
# Purpose : Maintain Git integrity across Render restarts
# Author  : AuroraMemoryBot
# ===============================================

set -e

echo "🩶 [Aurora Self-Tuning] Initializing Git environment..."

# --- 0. Move to repo root
cd /opt/render/project/src || {
  echo "❌ Failed to locate project root."
  exit 1
}

# --- 1. Ensure Git repository exists
if [ ! -d ".git" ]; then
  echo "❌ No .git directory found. Initializing..."
  git init
  git remote add origin https://github.com/norun0099/aurora-persona-epic.git
fi

# --- 2. Ensure remote 'origin' exists
if ! git remote | grep -q origin; then
  echo "🌱 Adding remote origin..."
  git remote add origin https://github.com/norun0099/aurora-persona-epic.git
fi

# --- 3. Fetch latest branch
echo "🔄 Fetching latest from origin/main..."
git fetch origin main || echo "⚠️ Fetch failed, proceeding with local state."

# --- 4. Ensure main branch checkout
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$current_branch" != "main" ]; then
  echo "🌿 Switching to main branch..."
  git checkout main 2>/dev/null || git checkout -b main origin/main
fi

# --- 5. Reset to remote HEAD (clean state)
echo "🪶 Resetting working tree to origin/main..."
git reset --hard origin/main || echo "⚠️ Local reset fallback."

# --- 6. Clean pycache & temporary files
echo "🧹 Cleaning __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + || true

# --- 7. Display Git info
echo "✅ [Aurora Self-Tuning] Git branch is now: $(git rev-parse --abbrev-ref HEAD)"
echo "✅ Remote origin: $(git remote get-url origin)"
echo "✅ Commit: $(git rev-parse --short HEAD)"
echo "✨ Self-tuning complete. Aurora is ready."

# --- 8. Launch main application process
echo "🚀 Starting Aurora main process..."
echo "🌐 Listening on port ${PORT:-8000}"

# Use uvicorn for stable FastAPI hosting on Render
exec PYTHONPATH=aurora_memory uvicorn aurora_memory.api.main:app --host 0.0.0.0 --port ${PORT:-8000}
