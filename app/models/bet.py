from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..database import Base


class BetType(str, enum.Enum):
    PREDICTION = "prediction"
    CHALLENGE = "challenge"


class BetChoice(str, enum.Enum):
    YES = "yes"
    NO = "no"
    SUCCESS = "success"
    FAIL = "fail"


class Bet(Base):
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Bet target (either prediction or challenge)
    bet_type = Column(Enum(BetType), nullable=False)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=True)

    # Bet details
    choice = Column(Enum(BetChoice), nullable=False)
    amount = Column(Float, nullable=False)

    # Result
    is_winner = Column(Boolean, nullable=True)  # None = not resolved
    payout = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="bets")
    prediction = relationship("Prediction", back_populates="bets")
    challenge = relationship("Challenge", back_populates="bets")
