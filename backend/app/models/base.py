"""
Database Models Base Module

Imports all models to ensure they're registered with SQLAlchemy.
"""

from app.core.database import Base
from app.models.user import User
from app.models.match import Match
from app.models.prediction import Prediction
from app.models.ai_prediction import AIPrediction
from app.models.league import League, LeagueMembership
from app.models.simulation import SimulationResult

__all__ = [
    "Base",
    "User",
    "Match",
    "Prediction",
    "AIPrediction",
    "League",
    "LeagueMembership",
    "SimulationResult"
]
