#!/bin/bash

# Agent-OS Desktop Launcher

AGENT_OS_DIR="/home/andy/proj/agent-os"
VENV_ACTIVATE="$AGENT_OS_DIR/venv/bin/activate"

cd "$AGENT_OS_DIR" || exit 1

# Check for required tools
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed or not in PATH."
    exit 1
fi

if ! command -v google-chrome &> /dev/null; then
    echo "Error: google-chrome is not installed or not in PATH."
    exit 1
fi

# Cleanup function
cleanup() {
    echo "Shutting down Agent-OS..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# Activate virtual environment
if [ -f "$VENV_ACTIVATE" ]; then
    source "$VENV_ACTIVATE"
else
    echo "Virtual environment not found at $VENV_ACTIVATE"
    exit 1
fi

echo "Starting Agent-OS Backend..."
# Start backend
python3 src/interface/server.py > server.log 2>&1 &
BACKEND_PID=$!

echo "Starting Agent-OS Frontend..."
# Start frontend
cd frontend
npm run dev -- --port 5173 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

wait_for_port() {
    local port=$1
    local name=$2
    local retries=30
    local wait_time=1

    echo "Waiting for $name on port $port..."
    while ! nc -z localhost $port; do
        ((retries--))
        if [ $retries -le 0 ]; then
            echo "Error: $name failed to start on port $port."
            return 1
        fi
        sleep $wait_time
    done
    echo "$name is ready!"
    return 0
}

# Wait for backend
wait_for_port 8000 "Backend" || cleanup

# Wait for frontend
wait_for_port 5173 "Frontend" || cleanup

echo "Launching UI..."
# Open in Chrome App Mode
# Using 0.0.0.0 or localhost depending on preference, but localhost is standard for local app
google-chrome --app=http://localhost:5173

# Wait for background processes
wait
