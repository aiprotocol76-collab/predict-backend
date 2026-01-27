from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse, UserUpdate, LeaderboardEntry

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse)
def create_or_get_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user or return existing one by wallet address."""
    user = db.query(User).filter(User.wallet_address == user_data.wallet_address).first()

    if user:
        return user

    user = User(
        wallet_address=user_data.wallet_address,
        username=user_data.username
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{wallet_address}", response_model=UserResponse)
def get_user(wallet_address: str, db: Session = Depends(get_db)):
    """Get user by wallet address."""
    user = db.query(User).filter(User.wallet_address == wallet_address).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{wallet_address}", response_model=UserResponse)
def update_user(wallet_address: str, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Update user profile."""
    user = db.query(User).filter(User.wallet_address == wallet_address).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.username:
        # Check if username is taken
        existing = db.query(User).filter(
            User.username == user_data.username,
            User.id != user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        user.username = user_data.username

    db.commit()
    db.refresh(user)
    return user


@router.get("/leaderboard/top", response_model=List[LeaderboardEntry])
def get_leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    """Get top users by prophet score."""
    users = db.query(User).order_by(User.prophet_score.desc()).limit(limit).all()

    return [
        LeaderboardEntry(rank=i + 1, user=user)
        for i, user in enumerate(users)
    ]
