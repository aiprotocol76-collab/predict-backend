from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..models.challenge import ChallengeCategory, ChallengeStatus


class ChallengeCreate(BaseModel):
    goal: str
    description: Optional[str] = None
    category: ChallengeCategory
    stake_amount: float
    ends_at: datetime
    verification_method: Optional[str] = None


class ChallengeUpdate(BaseModel):
    progress: Optional[float] = None
    progress_notes: Optional[str] = None
    status: Optional[ChallengeStatus] = None
    verification_proof: Optional[str] = None


class ChallengeResponse(BaseModel):
    id: int
    challenger_id: int
    challenger_address: Optional[str] = None
    challenger_username: Optional[str] = None
    goal: str
    description: Optional[str]
    category: ChallengeCategory
    status: ChallengeStatus
    stake_amount: float
    success_pool: float
    fail_pool: float
    total_pool: float
    success_percent: float
    fail_percent: float
    progress: float
    is_active: bool
    ends_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
