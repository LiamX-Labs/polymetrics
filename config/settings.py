"""
Polymetrics Platform Configuration
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'database' / 'polymetrics.db'))
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Data directories
DATA_DIR = BASE_DIR / 'data'
REPORTS_DIR = BASE_DIR / 'reports'
TEMPLATES_DIR = BASE_DIR / 'templates'

# API Configuration
POLYGONSCAN_API_KEY = os.getenv('POLYGONSCAN_API_KEY', 'ZA1X87TCSVVD53WECWZZ8UWJ7Y1VPKJ94A')
POLYMARKET_API_BASE = 'https://clob.polymarket.com'
GAMMA_API_BASE = 'https://gamma-api.polymarket.com'

# Cache settings
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
WALLET_CACHE_TIMEOUT = 3600  # 1 hour

# Pagination
POSITIONS_PER_PAGE = 50
LEADERBOARD_SIZE = 100
TOP_TRADERS_DISPLAY = 10

# Performance thresholds for classification
HFT_THRESHOLD_TRADES_PER_HOUR = 10
ACTIVE_TRADER_THRESHOLD = 100  # Total positions

# Flask settings
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

# Theme colors (from report template)
THEME = {
    'primary_purple': '#7C3AED',
    'secondary_purple': '#5B21B6',
    'dark_purple': '#4C1D95',
    'primary_orange': '#F97316',
    'secondary_orange': '#FB923C',
    'success_color': '#10B981',
    'danger_color': '#EF4444',
    'warning_color': '#F59E0B',
    'bg_color': '#0F0A1E',
    'text_primary': '#E5E7EB',
    'text_secondary': '#9CA3AF',
}
