"""
Market Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.database import Base


class Market(Base):
    __tablename__ = 'markets'

    id = Column(Integer, primary_key=True)
    condition_id = Column(String(66), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    event_slug = Column(String(255))
    end_date = Column(DateTime, index=True)
    category = Column(String(100))

    # Aggregated stats
    total_traders = Column(Integer, default=0)
    total_volume = Column(Float, default=0.0)
    avg_pnl = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Market {self.title[:30]}...>'

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'condition_id': self.condition_id,
            'title': self.title,
            'event_slug': self.event_slug,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'category': self.category,
            'total_traders': self.total_traders,
            'total_volume': round(self.total_volume, 2),
            'avg_pnl': round(self.avg_pnl, 2),
        }
