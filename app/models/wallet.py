"""
Wallet Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Wallet(Base):
    __tablename__ = 'wallets'

    id = Column(Integer, primary_key=True)
    address = Column(String(42), unique=True, nullable=False, index=True)
    first_analyzed = Column(DateTime, default=datetime.utcnow)
    last_analyzed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Performance metrics
    total_positions = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0, index=True)
    win_rate = Column(Float, default=0.0, index=True)
    profit_factor = Column(Float, default=0.0, index=True)
    risk_reward_ratio = Column(Float, default=0.0)
    trading_style = Column(String(20), default='unknown')
    is_active = Column(Boolean, default=True)

    # Additional metrics
    total_wins = Column(Float, default=0.0)
    total_losses = Column(Float, default=0.0)
    avg_win = Column(Float, default=0.0)
    avg_loss = Column(Float, default=0.0)
    best_trade = Column(Float, default=0.0)
    worst_trade = Column(Float, default=0.0)
    avg_position_size = Column(Float, default=0.0)
    total_volume = Column(Float, default=0.0)

    # Relationships
    positions = relationship('Position', back_populates='wallet', cascade='all, delete-orphan')
    snapshots = relationship('WalletSnapshot', back_populates='wallet', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Wallet {self.address[:10]}... PnL: ${self.total_pnl:.2f}>'

    @property
    def short_address(self):
        """Return shortened wallet address"""
        return f"{self.address[:6]}...{self.address[-4:]}"

    @property
    def num_wins(self):
        """Count winning positions"""
        return sum(1 for p in self.positions if p.realized_pnl > 0)

    @property
    def num_losses(self):
        """Count losing positions"""
        return sum(1 for p in self.positions if p.realized_pnl < 0)

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'address': self.address,
            'short_address': self.short_address,
            'first_analyzed': self.first_analyzed.isoformat() if self.first_analyzed else None,
            'last_analyzed': self.last_analyzed.isoformat() if self.last_analyzed else None,
            'total_positions': self.total_positions,
            'total_pnl': round(self.total_pnl, 2),
            'win_rate': round(self.win_rate, 2),
            'profit_factor': round(self.profit_factor, 2),
            'risk_reward_ratio': round(self.risk_reward_ratio, 2),
            'trading_style': self.trading_style,
            'total_wins': round(self.total_wins, 2),
            'total_losses': round(self.total_losses, 2),
            'avg_win': round(self.avg_win, 2),
            'avg_loss': round(self.avg_loss, 2),
            'best_trade': round(self.best_trade, 2),
            'worst_trade': round(self.worst_trade, 2),
            'avg_position_size': round(self.avg_position_size, 2),
            'total_volume': round(self.total_volume, 2),
        }
