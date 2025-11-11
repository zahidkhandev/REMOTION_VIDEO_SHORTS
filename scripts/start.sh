#!/bin/bash

# Start all development servers in parallel
echo "🚀 Starting Paper-to-Video Automator..."

# Function to kill all background processes on exit
cleanup() {
    echo "Stopping all services..."
    kill $(jobs -p) 2>/dev/null
}
trap cleanup EXIT

# Start backend
echo "Starting backend on http://localhost:8000..."
# Assuming your venv is at .venv in the procject root
(cd backend && source ../.venv/bin/activate && python -m app.main) &

# Start Remotion Studio (Frontend UI)
echo "Starting Remotion UI on http://localhost:5173..."
(cd frontend/video && npm run start) &

# Wait for all background processes
wait