#!/usr/bin/env bash
# HeartSync Start Script
# Activates venv and launches the Flask server

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Activate virtual environment
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
elif [ -f .venv/Scripts/activate ]; then
    source .venv/Scripts/activate
else
    echo "Error: Virtual environment not found. Run ./scripts/setup.sh first."
    exit 1
fi

echo "Starting HeartSync server..."
cd server
python app.py
