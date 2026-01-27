from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..models.user import UserTier


class UserCreate(BaseModel):
    wallet_address: str
    username: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    wallet_address: str
    username: Optional[str]
    prophet_score: float
    total_predictions: int
    correct_predictions: int
    accuracy: float
    total_earnings: float
    tier: UserTier
    created_at: datetime

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    rank: int
    user: UserResponse
