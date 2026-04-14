"""
User Model

Represents registered users in the platform.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class User(Base):
    """User model for authentication and profile management"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # User metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Scoring
    total_points = Column(Integer, default=0, nullable=False)
    predictions_count = Column(Integer, default=0, nullable=False)
    correct_results = Column(Integer, default=0, nullable=False)
    exact_scores = Column(Integer, default=0, nullable=False)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    league_memberships = relationship("LeagueMembership", back_populates="user", cascade="all, delete-orphan")
    owned_leagues = relationship("League", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', points={self.total_points})>"
    
    @property
    def accuracy(self) -> float:
        """Calculate prediction accuracy"""
        if self.predictions_count == 0:
            return 0.0
        return (self.correct_results / self.predictions_count) * 100
    
    @property
    def exact_score_rate(self) -> float:
        """Calculate exact score prediction rate"""
        if self.predictions_count == 0:
            return 0.0
        return (self.exact_scores / self.predictions_count) * 100
