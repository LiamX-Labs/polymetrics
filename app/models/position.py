"""
Position Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Position(Base):
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey('wallets.id'), nullable=False, index=True)
    condition_id = Column(String(66), nullable=False, index=True)
    market_title = Column(Text, nullable=False)
    outcome = Column(String(10), nullable=False)
    side = Column(String(10), nullable=False)

    # Position details
    avg_entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    position_size = Column(Float, nullable=False)
    realized_pnl = Column(Float, nullable=False, index=True)
    roi = Column(Float)

    # Trading info
    num_trades = Column(Integer, default=1)
    open_timestamp = Column(DateTime)
    close_timestamp = Column(DateTime, index=True)

    # Market info
    event_slug = Column(String(255))
    end_date = Column(DateTime)

    # Relationships
    wallet = relationship('Wallet', back_populates='positions')

    def __repr__(self):
        return f'<Position {self.market_title[:30]}... PnL: ${self.realized_pnl:.2f}>'

    @property
    def is_winner(self):
        """Check if position is profitable"""
        return self.realized_pnl > 0

    @property
    def short_market_title(self):
        """Return shortened market title"""
        if len(self.market_title) > 50:
            return f"{self.market_title[:47]}..."
        return self.market_title

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'wallet_id': self.wallet_id,
            'condition_id': self.condition_id,
            'market_title': self.market_title,
            'outcome': self.outcome,
            'side': self.side,
            'avg_entry_price': round(self.avg_entry_price, 4),
            'exit_price': round(self.exit_price, 4) if self.exit_price else None,
            'position_size': round(self.position_size, 2),
            'realized_pnl': round(self.realized_pnl, 2),
            'roi': round(self.roi, 2) if self.roi else None,
            'num_trades': self.num_trades,
            'open_timestamp': self.open_timestamp.isoformat() if self.open_timestamp else None,
            'close_timestamp': self.close_timestamp.isoformat() if self.close_timestamp else None,
            'event_slug': self.event_slug,
            'end_date': self.end_date.isoformat() if self.end_date else None,
        }
