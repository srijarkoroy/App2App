#!/bin/bash
set -e

echo "🚀 Installing dependencies..."
pip install -r requirements.txt

echo "🎭 Installing Playwright browsers..."
playwright install --with-deps

echo "✅ Installation complete!"