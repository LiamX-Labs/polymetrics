#!/usr/bin/env python3
"""
Polymetrics Application Entry Point
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from config import settings

app = create_app()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Polymetrics - Polymarket Analytics Platform")
    print("="*60)
    print(f"\nServer running at: http://{settings.HOST}:{settings.PORT}")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"Database: {settings.DATABASE_PATH}")
    print("\nPress CTRL+C to stop the server\n")

    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG
    )
