#!/bin/bash

# Agent-OS Server Launcher (Headless)

AGENT_OS_DIR="/home/andy/proj/agent-os"
VENV_ACTIVATE="$AGENT_OS_DIR/venv/bin/activate"

# Ensure we use the correct Node version from NVM
export PATH="/home/andy/.nvm/versions/node/v22.20.0/bin:$PATH"

cd "$AGENT_OS_DIR" || exit 1

# Check for required tools
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed or not in PATH."
    exit 1
fi

# Activate virtual environment
if [ -f "$VENV_ACTIVATE" ]; then
    source "$VENV_ACTIVATE"
else
    echo "Virtual environment not found at $VENV_ACTIVATE"
    exit 1
fi

# Cleanup function
cleanup() {
    echo "Shutting down Agent-OS Server..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

echo "Starting Agent-OS Backend..."
# Start backend
python3 src/interface/server.py 2>&1 | tee server.log &
BACKEND_PID=$!

echo "Starting Agent-OS Frontend..."
# Start frontend
cd frontend
npm run dev -- --host --port 5173 2>&1 | tee ../frontend.log &
FRONTEND_PID=$!
cd ..

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
