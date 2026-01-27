from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..database import Base


class PredictionCategory(str, enum.Enum):
    CRYPTO = "crypto"
    TECH = "tech"
    SPORTS = "sports"
    POLITICS = "politics"
    ENTERTAINMENT = "entertainment"


class PredictionStatus(str, enum.Enum):
    ACTIVE = "active"
    RESOLVED_YES = "resolved_yes"
    RESOLVED_NO = "resolved_no"
    CANCELLED = "cancelled"


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(PredictionCategory), nullable=False)
    status = Column(Enum(PredictionStatus), default=PredictionStatus.ACTIVE)

    # AI prediction
    ai_prediction = Column(String, nullable=True)  # "yes" or "no"
    ai_confidence = Column(Float, nullable=True)  # 0-100

    # Betting pools
    yes_pool = Column(Float, default=0)
    no_pool = Column(Float, default=0)

    # Resolution
    resolution_source = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    # Timestamps
    ends_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bets = relationship("Bet", back_populates="prediction")

    @property
    def total_pool(self) -> float:
        return self.yes_pool + self.no_pool

    @property
    def yes_percent(self) -> float:
        if self.total_pool == 0:
            return 50
        return (self.yes_pool / self.total_pool) * 100

    @property
    def no_percent(self) -> float:
        if self.total_pool == 0:
            return 50
        return (self.no_pool / self.total_pool) * 100

    @property
    def is_active(self) -> bool:
        return self.status == PredictionStatus.ACTIVE and datetime.utcnow() < self.ends_at
