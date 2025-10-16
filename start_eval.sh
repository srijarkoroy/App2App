#!/bin/bash
set -e

echo "🧠 Installing Playwright browsers..."
python -m playwright install --with-deps || true

echo "🚀 Starting Evaluation Server..."
exec uvicorn tests.eval_server:app --host 0.0.0.0 --port ${PORT:-8000}