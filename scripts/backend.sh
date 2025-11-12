#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "Navigating to backend directory..."
# Assumes this script is run from the project root
cd backend

echo "Activating Python virtual environment..."
# Check for both standard Unix and Windows Git Bash venv paths
if [ -f ".venv/bin/activate" ]; then
    echo "Activating Unix-style venv: .venv/bin/activate"
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    echo "Activating Windows-style venv: .venv/Scripts/activate"
    source .venv/Scripts/activate
else
    echo "Warning: Could not find virtual environment."
    echo "Please activate your '.venv' manually before running this."
fi

echo "Starting Uvicorn server at http://0.0.0.0:8000..."
# We explicitly set host and port
uvicorn app.main:app --host 0.0.0.0 --port 8000