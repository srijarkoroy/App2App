#!/bin/bash
set -e

echo "🚀 Installing python dependencies..."
pip install -r requirements.txt

echo "🎭 Installing Playwright browsers..."
playwright install chromium

echo "✅ Installation complete!"