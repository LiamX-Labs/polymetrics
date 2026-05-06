"""
Database initialization and utilities
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from config import settings

# Create base class for models
Base = declarative_base()

# Database engine
engine = None
db_session = None


def init_db(app=None):
    """Initialize database connection and create tables"""
    global engine, db_session

    db_uri = settings.SQLALCHEMY_DATABASE_URI
    if app:
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']

    engine = create_engine(db_uri, echo=settings.DEBUG)
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    Base.query = db_session.query_property()

    # Import all models to ensure they're registered
    from app.models import Wallet, Position, Market, WalletSnapshot, LeaderboardCache

    # Create all tables
    Base.metadata.create_all(bind=engine)

    return db_session


def get_session():
    """Get database session"""
    return db_session


def close_db():
    """Close database connection"""
    if db_session:
        db_session.remove()
