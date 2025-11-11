#!/bin/bash
set -e

echo "🚀 Setting up Paper-to-Video Automator..."

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup Remotion
echo "🎬 Setting up Remotion..."
cd frontend/video
npm install
cd ../..

# Setup UI
echo "🎨 Setting up UI..."
cd frontend/ui
npm install
cd ../..

# Create storage directories
echo "📁 Creating storage directories..."
mkdir -p backend/storage/{audio,props,videos}
mkdir -p frontend/video/public/audio

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your .env file with API keys"
echo "2. Run './scripts/dev.sh' to start all services"
