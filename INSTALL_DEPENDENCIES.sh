#!/bin/bash

echo "📦 Installing Polymetrics Platform Dependencies..."
echo ""

# Activate venv
source venv/bin/activate

# Install all required packages
pip install -q \
    Flask \
    Flask-SQLAlchemy \
    Flask-CORS \
    requests \
    pandas \
    numpy

echo ""
echo "✅ All dependencies installed successfully!"
echo ""
echo "You can now run: ./RUN_PLATFORM.sh"
