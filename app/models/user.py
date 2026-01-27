from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..database import Base


class UserTier(str, enum.Enum):
    NOVICE = "novice"
    SEER = "seer"
    ORACLE = "oracle"
    PROPHET = "prophet"
    GRAND = "grand"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)

    # Stats
    prophet_score = Column(Float, default=0)
    total_predictions = Column(Integer, default=0)
    correct_predictions = Column(Integer, default=0)
    total_earnings = Column(Float, default=0)
    tier = Column(Enum(UserTier), default=UserTier.NOVICE)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bets = relationship("Bet", back_populates="user")
    challenges = relationship("Challenge", back_populates="challenger")

    @property
    def accuracy(self) -> float:
        if self.total_predictions == 0:
            return 0
        return (self.correct_predictions / self.total_predictions) * 100

    def calculate_tier(self):
        if self.prophet_score >= 1000:
            self.tier = UserTier.GRAND if self.prophet_score >= 2000 else UserTier.PROPHET
        elif self.prophet_score >= 500:
            self.tier = UserTier.ORACLE
        elif self.prophet_score >= 100:
            self.tier = UserTier.SEER
        else:
            self.tier = UserTier.NOVICE
