#!/bin/bash
set -e

echo "🧠 Installing Playwright browsers..."
playwright install chromium

echo "🚀 Starting Main API..."
exec uvicorn api.main:app --host 0.0.0.0 --port $PORT