#!/bin/bash

# Navigate to the directory where start.sh is located
cd "$(dirname "$0")"

echo "=========================================="
echo "🚀 Starting Coder-Bot Ecosystem..."
echo "=========================================="

# Trap Ctrl+C (SIGINT) and SIGTERM to kill background tasks on exit
cleanup() {
    echo -e "\n🛑 Shutdown signal received! Stopping all processes..."
    kill $(jobs -p) 2>/dev/null
    echo "👋 All services stopped cleanly."
    exit 0
}

trap cleanup SIGINT SIGTERM

# 1. Start FastAPI Web Server in the background
echo "📡 Launching API Server (api_server.py)..."
python3 api_server.py &

# Wait a brief moment for FastAPI to initialize
sleep 2

# 2. Start Discord Bot in the foreground
echo "🤖 Launching Discord Bot (main.py)..."
python3 main.py

# If main.py finishes or exits, clean up background tasks
cleanup
