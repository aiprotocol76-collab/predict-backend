from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .api import users, predictions, challenges, bets

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PREDICT API",
    description="AI-Powered Prediction Platform API",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://app-iota-seven-24.vercel.app",
        "https://predict-website.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(challenges.router, prefix="/api/v1")
app.include_router(bets.router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "name": "PREDICT API",
        "version": "1.0.0",
        "description": "AI-Powered Prediction Platform",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/v1/stats")
def get_stats():
    """Get platform statistics."""
    # TODO: Calculate from database
    return {
        "total_predictions": 1234,
        "total_challenges": 567,
        "total_staked": 1200000,
        "ai_accuracy": 73,
        "total_users": 890,
    }
