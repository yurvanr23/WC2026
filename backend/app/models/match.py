"""
Match Model

Represents World Cup matches.
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class MatchStatus(str, enum.Enum):
    """Match status enumeration"""
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class TournamentStage(str, enum.Enum):
    """Tournament stage enumeration"""
    GROUP = "group"
    ROUND_16 = "round_16"
    QUARTER = "quarter"
    SEMI = "semi"
    THIRD_PLACE = "third_place"
    FINAL = "final"


class Match(Base):
    """Match model representing World Cup fixtures"""
    
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Team information
    home_team = Column(String(100), nullable=False, index=True)
    away_team = Column(String(100), nullable=False, index=True)
    
    # Match details
    match_date = Column(DateTime, nullable=False, index=True)
    venue = Column(String(200))
    stage = Column(SQLEnum(TournamentStage), nullable=False, index=True)
    group_name = Column(String(10))  # e.g., "Group A"
    
    # Scores
    home_score = Column(Integer)
    away_score = Column(Integer)
    home_penalties = Column(Integer)  # For knockout stages
    away_penalties = Column(Integer)
    
    # Status
    status = Column(SQLEnum(MatchStatus), default=MatchStatus.SCHEDULED, nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="match", cascade="all, delete-orphan")
    ai_predictions = relationship("AIPrediction", back_populates="match", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Match(id={self.id}, {self.home_team} vs {self.away_team}, {self.stage.value})>"
    
    @property
    def is_finished(self) -> bool:
        """Check if match is finished"""
        return self.status == MatchStatus.FINISHED
    
    @property
    def result(self) -> str:
        """Get match result (H/D/A)"""
        if not self.is_finished or self.home_score is None or self.away_score is None:
            return None
        
        if self.home_score > self.away_score:
            return "H"  # Home win
        elif self.home_score < self.away_score:
            return "A"  # Away win
        else:
            return "D"  # Draw
    
    @property
    def total_goals(self) -> int:
        """Get total goals in the match"""
        if self.home_score is None or self.away_score is None:
            return 0
        return self.home_score + self.away_score
    
    @property
    def is_upcoming(self) -> bool:
        """Check if match is upcoming"""
        return self.match_date > datetime.utcnow() and self.status == MatchStatus.SCHEDULED
