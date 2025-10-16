#!/bin/bash
set -e

echo "🧠 Installing Playwright browsers..."
playwright install --with-deps

echo "🚀 Starting Main API..."
exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}