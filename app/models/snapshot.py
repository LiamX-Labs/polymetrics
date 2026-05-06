"""
Wallet Snapshot Model for Historical Tracking
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class WalletSnapshot(Base):
    __tablename__ = 'wallet_snapshots'

    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey('wallets.id'), nullable=False)
    snapshot_date = Column(DateTime, default=datetime.utcnow)

    total_positions = Column(Integer)
    total_pnl = Column(Float)
    win_rate = Column(Float)
    profit_factor = Column(Float)

    # Relationships
    wallet = relationship('Wallet', back_populates='snapshots')

    def __repr__(self):
        return f'<Snapshot Wallet#{self.wallet_id} {self.snapshot_date}>'

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'wallet_id': self.wallet_id,
            'snapshot_date': self.snapshot_date.isoformat(),
            'total_positions': self.total_positions,
            'total_pnl': round(self.total_pnl, 2) if self.total_pnl else 0,
            'win_rate': round(self.win_rate, 2) if self.win_rate else 0,
            'profit_factor': round(self.profit_factor, 2) if self.profit_factor else 0,
        }
