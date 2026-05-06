"""
Polymetrics Flask Application
"""
from flask import Flask
from flask_cors import CORS
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from app.database import init_db, close_db


def create_app():
    """Application factory"""
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # Load configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['DEBUG'] = settings.DEBUG

    # Enable CORS
    CORS(app)

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize database
    with app.app_context():
        init_db(app)

    # Register blueprints
    from app.routes import home, wallet, api, compare

    app.register_blueprint(home.bp)
    app.register_blueprint(wallet.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(compare.bp)

    # Start background scheduler for leaderboard refresh
    from app.services.scheduler import start_scheduler
    start_scheduler()
    logging.info("Background scheduler started - leaderboard will refresh hourly")

    # Teardown
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        close_db()

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500

    return app
