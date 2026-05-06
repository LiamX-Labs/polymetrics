"""
Leaderboard Cache Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base


class LeaderboardCache(Base):
    __tablename__ = 'leaderboard_cache'

    id = Column(Integer, primary_key=True)
    metric_name = Column(String(50), nullable=False, index=True)
    wallet_address = Column(String(42), nullable=False)
    metric_value = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Leaderboard {self.metric_name} Rank#{self.rank}>'

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'metric_name': self.metric_name,
            'wallet_address': self.wallet_address,
            'metric_value': round(self.metric_value, 2),
            'rank': self.rank,
            'updated_at': self.updated_at.isoformat(),
        }
