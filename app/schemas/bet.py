from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..models.bet import BetType, BetChoice


class BetCreate(BaseModel):
    bet_type: BetType
    prediction_id: Optional[int] = None
    challenge_id: Optional[int] = None
    choice: BetChoice
    amount: float


class BetResponse(BaseModel):
    id: int
    user_id: int
    bet_type: BetType
    prediction_id: Optional[int]
    challenge_id: Optional[int]
    choice: BetChoice
    amount: float
    is_winner: Optional[bool]
    payout: Optional[float]
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True
