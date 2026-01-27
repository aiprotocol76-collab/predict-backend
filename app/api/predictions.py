from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.prediction import Prediction, PredictionCategory, PredictionStatus
from ..schemas.prediction import PredictionCreate, PredictionResponse, PredictionUpdate

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("/", response_model=PredictionResponse)
def create_prediction(prediction_data: PredictionCreate, db: Session = Depends(get_db)):
    """Create a new prediction."""
    prediction = Prediction(
        question=prediction_data.question,
        description=prediction_data.description,
        category=prediction_data.category,
        ends_at=prediction_data.ends_at,
        ai_prediction=prediction_data.ai_prediction,
        ai_confidence=prediction_data.ai_confidence,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


@router.get("/", response_model=List[PredictionResponse])
def get_predictions(
    category: Optional[PredictionCategory] = None,
    status: Optional[PredictionStatus] = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get all predictions with optional filters."""
    query = db.query(Prediction)

    if category:
        query = query.filter(Prediction.category == category)

    if status:
        query = query.filter(Prediction.status == status)

    if active_only:
        query = query.filter(
            Prediction.status == PredictionStatus.ACTIVE,
            Prediction.ends_at > datetime.utcnow()
        )

    predictions = query.order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()
    return predictions


@router.get("/{prediction_id}", response_model=PredictionResponse)
def get_prediction(prediction_id: int, db: Session = Depends(get_db)):
    """Get a specific prediction."""
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return prediction


@router.put("/{prediction_id}", response_model=PredictionResponse)
def update_prediction(
    prediction_id: int,
    prediction_data: PredictionUpdate,
    db: Session = Depends(get_db)
):
    """Update a prediction (admin only in production)."""
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    if prediction_data.question is not None:
        prediction.question = prediction_data.question
    if prediction_data.description is not None:
        prediction.description = prediction_data.description
    if prediction_data.status is not None:
        prediction.status = prediction_data.status
        if prediction_data.status in [PredictionStatus.RESOLVED_YES, PredictionStatus.RESOLVED_NO]:
            prediction.resolved_at = datetime.utcnow()
    if prediction_data.ai_prediction is not None:
        prediction.ai_prediction = prediction_data.ai_prediction
    if prediction_data.ai_confidence is not None:
        prediction.ai_confidence = prediction_data.ai_confidence

    db.commit()
    db.refresh(prediction)
    return prediction


@router.post("/{prediction_id}/resolve")
def resolve_prediction(
    prediction_id: int,
    outcome: str = Query(..., regex="^(yes|no)$"),
    db: Session = Depends(get_db)
):
    """Resolve a prediction (admin only in production)."""
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    if prediction.status != PredictionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Prediction is not active")

    prediction.status = PredictionStatus.RESOLVED_YES if outcome == "yes" else PredictionStatus.RESOLVED_NO
    prediction.resolved_at = datetime.utcnow()

    # TODO: Process payouts to winners

    db.commit()
    return {"message": f"Prediction resolved as {outcome}", "prediction_id": prediction_id}
