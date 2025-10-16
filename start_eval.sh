#!/bin/bash
set -e

echo "🧠 Installing Playwright browsers..."
playwright install chromium

echo "🚀 Starting Evaluation Server..."
exec uvicorn tests.eval_server:app --host 0.0.0.0 --port $PORT