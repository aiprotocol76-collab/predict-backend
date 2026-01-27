from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.challenge import Challenge, ChallengeCategory, ChallengeStatus
from ..models.user import User
from ..schemas.challenge import ChallengeCreate, ChallengeResponse, ChallengeUpdate

router = APIRouter(prefix="/challenges", tags=["challenges"])


def challenge_to_response(challenge: Challenge) -> dict:
    """Convert challenge model to response with challenger info."""
    return {
        "id": challenge.id,
        "challenger_id": challenge.challenger_id,
        "challenger_address": challenge.challenger.wallet_address if challenge.challenger else None,
        "challenger_username": challenge.challenger.username if challenge.challenger else None,
        "goal": challenge.goal,
        "description": challenge.description,
        "category": challenge.category,
        "status": challenge.status,
        "stake_amount": challenge.stake_amount,
        "success_pool": challenge.success_pool,
        "fail_pool": challenge.fail_pool,
        "total_pool": challenge.total_pool,
        "success_percent": challenge.success_percent,
        "fail_percent": challenge.fail_percent,
        "progress": challenge.progress,
        "is_active": challenge.is_active,
        "ends_at": challenge.ends_at,
        "created_at": challenge.created_at,
    }


@router.post("/", response_model=ChallengeResponse)
def create_challenge(
    challenge_data: ChallengeCreate,
    wallet_address: str = Query(..., description="Challenger's wallet address"),
    db: Session = Depends(get_db)
):
    """Create a new personal challenge."""
    # Get or create user
    user = db.query(User).filter(User.wallet_address == wallet_address).first()
    if not user:
        user = User(wallet_address=wallet_address)
        db.add(user)
        db.commit()
        db.refresh(user)

    challenge = Challenge(
        challenger_id=user.id,
        goal=challenge_data.goal,
        description=challenge_data.description,
        category=challenge_data.category,
        stake_amount=challenge_data.stake_amount,
        ends_at=challenge_data.ends_at,
        verification_method=challenge_data.verification_method,
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge_to_response(challenge)


@router.get("/", response_model=List[ChallengeResponse])
def get_challenges(
    category: Optional[ChallengeCategory] = None,
    status: Optional[ChallengeStatus] = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get all challenges with optional filters."""
    query = db.query(Challenge)

    if category:
        query = query.filter(Challenge.category == category)

    if status:
        query = query.filter(Challenge.status == status)

    if active_only:
        query = query.filter(
            Challenge.status == ChallengeStatus.ACTIVE,
            Challenge.ends_at > datetime.utcnow()
        )

    challenges = query.order_by(Challenge.created_at.desc()).offset(skip).limit(limit).all()
    return [challenge_to_response(c) for c in challenges]


@router.get("/{challenge_id}", response_model=ChallengeResponse)
def get_challenge(challenge_id: int, db: Session = Depends(get_db)):
    """Get a specific challenge."""
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge_to_response(challenge)


@router.put("/{challenge_id}", response_model=ChallengeResponse)
def update_challenge(
    challenge_id: int,
    challenge_data: ChallengeUpdate,
    wallet_address: str = Query(..., description="Challenger's wallet address"),
    db: Session = Depends(get_db)
):
    """Update challenge progress (only by challenger)."""
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    if challenge.challenger.wallet_address != wallet_address:
        raise HTTPException(status_code=403, detail="Only challenger can update")

    if challenge_data.progress is not None:
        challenge.progress = min(100, max(0, challenge_data.progress))
    if challenge_data.progress_notes is not None:
        challenge.progress_notes = challenge_data.progress_notes
    if challenge_data.verification_proof is not None:
        challenge.verification_proof = challenge_data.verification_proof

    db.commit()
    db.refresh(challenge)
    return challenge_to_response(challenge)


@router.post("/{challenge_id}/resolve")
def resolve_challenge(
    challenge_id: int,
    outcome: str = Query(..., regex="^(success|fail)$"),
    db: Session = Depends(get_db)
):
    """Resolve a challenge (admin only in production)."""
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    if challenge.status != ChallengeStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Challenge is not active")

    challenge.status = (
        ChallengeStatus.COMPLETED_SUCCESS if outcome == "success"
        else ChallengeStatus.COMPLETED_FAIL
    )

    # TODO: Process payouts

    db.commit()
    return {"message": f"Challenge resolved as {outcome}", "challenge_id": challenge_id}
