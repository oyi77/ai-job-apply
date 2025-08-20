#!/bin/bash

# AI Job Application Assistant - Startup Script
# This script sets up the environment and starts the application

set -e

echo "🚀 Starting AI Job Application Assistant Setup..."

# Check if Python 3.10+ is installed
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.10 or higher is required. Current version: $python_version"
    echo "Please upgrade Python and try again."
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -e .

# Install development dependencies if requested
if [ "$1" = "--dev" ]; then
    echo "🔧 Installing development dependencies..."
    pip install -e ".[dev]"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    if [ -f "config.env.example" ]; then
        cp config.env.example .env
        echo "⚠️  Please edit .env file and add your Gemini API key:"
        echo "   GEMINI_API_KEY=your_api_key_here"
        echo ""
        echo "Get your API key from: https://makersuite.google.com/app/apikey"
        echo ""
        read -p "Press Enter after adding your API key..."
    else
        echo "❌ Error: config.env.example not found!"
        exit 1
    fi
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs output resumes templates uploads

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

echo "✅ Setup completed successfully!"
echo ""
echo "🚀 Starting the application..."
echo "📝 Web interface will be available at: http://localhost:8000"
echo "📚 API documentation will be available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Start the application
python -m src.main 