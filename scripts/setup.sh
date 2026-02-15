#!/usr/bin/env bash
# HeartSync Setup Script
# Creates virtual environment and installs dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Setting up HeartSync..."

# Create virtual environment
cd "$PROJECT_DIR"
uv venv .venv
echo "Virtual environment created."

# Install dependencies
uv pip install -r requirements.txt
echo "Dependencies installed."

# Create directories if missing
mkdir -p audio display/assets hardware/arduino_led scripts docs/photos

# Copy .env.example if .env doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example — fill in your API keys!"
else
    echo ".env already exists, skipping."
fi

echo ""
echo "Setup complete! Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Place audio stems (harmony.wav, neutral.wav, tension.wav) in audio/"
echo "  3. Run: ./scripts/start.sh"
