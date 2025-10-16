#!/bin/bash
set -e

echo "🧠 Installing Playwright browsers..."
python -m playwright install --with-deps || true

echo "🚀 Starting Main API..."
exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}