from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..models.prediction import PredictionCategory, PredictionStatus


class PredictionCreate(BaseModel):
    question: str
    description: Optional[str] = None
    category: PredictionCategory
    ends_at: datetime
    ai_prediction: Optional[str] = None
    ai_confidence: Optional[float] = None


class PredictionUpdate(BaseModel):
    question: Optional[str] = None
    description: Optional[str] = None
    status: Optional[PredictionStatus] = None
    ai_prediction: Optional[str] = None
    ai_confidence: Optional[float] = None


class PredictionResponse(BaseModel):
    id: int
    question: str
    description: Optional[str]
    category: PredictionCategory
    status: PredictionStatus
    ai_prediction: Optional[str]
    ai_confidence: Optional[float]
    yes_pool: float
    no_pool: float
    total_pool: float
    yes_percent: float
    no_percent: float
    is_active: bool
    ends_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
