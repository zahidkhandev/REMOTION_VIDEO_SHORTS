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
(cd backend && source ../.venv/bin/activate && python -m app.main) &

# Start UI
echo "Starting UI on http://localhost:5173..."
(cd frontend/ui && npm run dev) &

# Wait for all background processes
wait
