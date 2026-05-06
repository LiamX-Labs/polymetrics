#!/bin/bash

# Polymetrics Platform Launcher
# Quick script to start the analytics platform

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║         📊 POLYMETRICS PLATFORM LAUNCHER 📊             ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create one first: python3 -m venv venv"
    exit 1
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if Flask is installed
echo "🔍 Checking dependencies..."
python -c "import flask; import pandas; import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing dependencies..."
    pip install Flask Flask-SQLAlchemy Flask-CORS requests pandas numpy -q
    echo "✅ Dependencies installed!"
else
    echo "✅ Dependencies OK!"
fi

echo ""
echo "🚀 Starting Polymetrics Platform..."
echo ""

# Run the platform
python run.py
