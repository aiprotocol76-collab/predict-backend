from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..models.bet import Bet, BetType, BetChoice
from ..models.prediction import Prediction, PredictionStatus
from ..models.challenge import Challenge, ChallengeStatus
from ..models.user import User
from ..schemas.bet import BetCreate, BetResponse

router = APIRouter(prefix="/bets", tags=["bets"])


@router.post("/", response_model=BetResponse)
def place_bet(
    bet_data: BetCreate,
    wallet_address: str = Query(..., description="Bettor's wallet address"),
    db: Session = Depends(get_db)
):
    """Place a bet on a prediction or challenge."""
    # Get or create user
    user = db.query(User).filter(User.wallet_address == wallet_address).first()
    if not user:
        user = User(wallet_address=wallet_address)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Validate bet target
    if bet_data.bet_type == BetType.PREDICTION:
        if not bet_data.prediction_id:
            raise HTTPException(status_code=400, detail="prediction_id required for prediction bets")

        prediction = db.query(Prediction).filter(Prediction.id == bet_data.prediction_id).first()
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")

        if not prediction.is_active:
            raise HTTPException(status_code=400, detail="Prediction is not active")

        if bet_data.choice not in [BetChoice.YES, BetChoice.NO]:
            raise HTTPException(status_code=400, detail="Choice must be 'yes' or 'no' for predictions")

        # Update pool
        if bet_data.choice == BetChoice.YES:
            prediction.yes_pool += bet_data.amount
        else:
            prediction.no_pool += bet_data.amount

    elif bet_data.bet_type == BetType.CHALLENGE:
        if not bet_data.challenge_id:
            raise HTTPException(status_code=400, detail="challenge_id required for challenge bets")

        challenge = db.query(Challenge).filter(Challenge.id == bet_data.challenge_id).first()
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")

        if not challenge.is_active:
            raise HTTPException(status_code=400, detail="Challenge is not active")

        if bet_data.choice not in [BetChoice.SUCCESS, BetChoice.FAIL]:
            raise HTTPException(status_code=400, detail="Choice must be 'success' or 'fail' for challenges")

        # Update pool
        if bet_data.choice == BetChoice.SUCCESS:
            challenge.success_pool += bet_data.amount
        else:
            challenge.fail_pool += bet_data.amount

    # Create bet
    bet = Bet(
        user_id=user.id,
        bet_type=bet_data.bet_type,
        prediction_id=bet_data.prediction_id,
        challenge_id=bet_data.challenge_id,
        choice=bet_data.choice,
        amount=bet_data.amount,
    )
    db.add(bet)

    # Update user stats
    user.total_predictions += 1

    db.commit()
    db.refresh(bet)
    return bet


@router.get("/user/{wallet_address}", response_model=List[BetResponse])
def get_user_bets(
    wallet_address: str,
    bet_type: BetType = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all bets for a user."""
    user = db.query(User).filter(User.wallet_address == wallet_address).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = db.query(Bet).filter(Bet.user_id == user.id)

    if bet_type:
        query = query.filter(Bet.bet_type == bet_type)

    bets = query.order_by(Bet.created_at.desc()).offset(skip).limit(limit).all()
    return bets


@router.get("/{bet_id}", response_model=BetResponse)
def get_bet(bet_id: int, db: Session = Depends(get_db)):
    """Get a specific bet."""
    bet = db.query(Bet).filter(Bet.id == bet_id).first()
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")
    return bet
