from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..database import Base


class ChallengeCategory(str, enum.Enum):
    HEALTH = "health"
    EDUCATION = "education"
    CAREER = "career"
    CREATIVE = "creative"
    FITNESS = "fitness"
    FINANCE = "finance"


class ChallengeStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED_SUCCESS = "completed_success"
    COMPLETED_FAIL = "completed_fail"
    CANCELLED = "cancelled"


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    challenger_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    goal = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(ChallengeCategory), nullable=False)
    status = Column(Enum(ChallengeStatus), default=ChallengeStatus.ACTIVE)

    # Challenger's stake
    stake_amount = Column(Float, nullable=False)

    # Betting pools
    success_pool = Column(Float, default=0)
    fail_pool = Column(Float, default=0)

    # Progress tracking (0-100)
    progress = Column(Float, default=0)
    progress_notes = Column(Text, nullable=True)

    # Verification
    verification_method = Column(String, nullable=True)
    verification_proof = Column(String, nullable=True)

    # Timestamps
    ends_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    challenger = relationship("User", back_populates="challenges")
    bets = relationship("Bet", back_populates="challenge")

    @property
    def total_pool(self) -> float:
        return self.success_pool + self.fail_pool + self.stake_amount

    @property
    def success_percent(self) -> float:
        total = self.success_pool + self.fail_pool
        if total == 0:
            return 50
        return (self.success_pool / total) * 100

    @property
    def fail_percent(self) -> float:
        total = self.success_pool + self.fail_pool
        if total == 0:
            return 50
        return (self.fail_pool / total) * 100

    @property
    def is_active(self) -> bool:
        return self.status == ChallengeStatus.ACTIVE and datetime.utcnow() < self.ends_at
