#!/bin/bash
set -e

echo "🌿 Starting Aurora initialization sequence..."

# 1. Ensure Git repository is clean and configured
if [ ! -d ".git" ]; then
  echo "📁 Initializing new git repository..."
  git init
  git remote add origin https://github.com/norun0099/aurora-persona-epic.git
else
  echo "📁 Existing git repository detected."
fi

# 2. Fetch latest from origin
echo "🌐 Fetching latest from origin..."
git fetch origin main || echo "⚠️  Warning: fetch failed (network or permissions issue)."

# 3. Checkout main branch and sync
if git rev-parse --verify main >/dev/null 2>&1; then
  echo "🔄 Checking out main branch..."
  git checkout main
else
  echo "🌱 Creating new main branch..."
  git checkout -b main
fi

# 4. Ensure tracking relationship
git branch --set-upstream-to=origin/main main || echo "ℹ️  Tracking setup skipped."

# 5. Reset to clean remote state (optional safe sync)
echo "🧹 Resetting repository to match remote (safe sync)..."
git reset --hard origin/main || echo "ℹ️  No remote reference, continuing with local state."

# --------------------------------------------------------
# 5.5 Inject authenticated remote URL (for push operations)
# --------------------------------------------------------
if [ -n "$GITHUB_TOKEN" ]; then
  echo "🔐 Injecting authenticated remote URL..."
  git remote set-url origin https://aurora-bot:${GITHUB_TOKEN}@github.com/norun0099/aurora-persona-epic.git
else
  echo "⚠️  GITHUB_TOKEN not found; push authentication may fail."
fi

# 6. Confirm configuration
git remote -v

# 7. Install dependencies if necessary
if [ -f "requirements.txt" ]; then
  echo "📦 Installing dependencies..."
  pip install -r requirements.txt --quiet
else
  echo "📦 No requirements.txt found, skipping installation."
fi

# 8. Launch Aurora (FastAPI or main entry)
echo "🚀 Launching Aurora server..."
exec uvicorn aurora_memory.api.main:app --host 0.0.0.0 --port 10000 --reload
