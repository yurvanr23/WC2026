"""
Prediction Model

Represents user predictions for matches.
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Prediction(Base):
    """Prediction model for user match predictions"""
    
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Prediction details
    predicted_home_score = Column(Integer, nullable=False)
    predicted_away_score = Column(Integer, nullable=False)
    confidence = Column(Integer, nullable=False)  # 0-100
    
    # Scoring
    points_earned = Column(Integer, default=0, nullable=False)
    is_scored = Column(Integer, default=False, nullable=False)  # Changed to Integer for SQLite compatibility
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('confidence >= 0 AND confidence <= 100', name='check_confidence_range'),
        CheckConstraint('predicted_home_score >= 0', name='check_home_score_positive'),
        CheckConstraint('predicted_away_score >= 0', name='check_away_score_positive'),
        UniqueConstraint('user_id', 'match_id', name='unique_user_match_prediction'),
    )
    
    # Relationships
    user = relationship("User", back_populates="predictions")
    match = relationship("Match", back_populates="predictions")
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, user={self.user_id}, match={self.match_id}, score={self.predicted_home_score}-{self.predicted_away_score})>"
    
    @property
    def predicted_result(self) -> str:
        """Get predicted result (H/D/A)"""
        if self.predicted_home_score > self.predicted_away_score:
            return "H"
        elif self.predicted_home_score < self.predicted_away_score:
            return "A"
        else:
            return "D"
    
    @property
    def predicted_total_goals(self) -> int:
        """Get predicted total goals"""
        return self.predicted_home_score + self.predicted_away_score
    
    def calculate_points(self, match) -> int:
        """
        Calculate points earned for this prediction.
        
        Args:
            match: Match object with actual results
            
        Returns:
            Points earned
        """
        from app.core.config import settings
        
        if not match.is_finished:
            return 0
        
        points = 0
        actual_result = match.result
        
        # Exact score prediction
        if (self.predicted_home_score == match.home_score and 
            self.predicted_away_score == match.away_score):
            points += settings.POINTS_EXACT_SCORE
            points += settings.POINTS_CORRECT_RESULT  # Also gets result points
        # Correct result (W/D/L)
        elif self.predicted_result == actual_result:
            points += settings.POINTS_CORRECT_RESULT
        # Correct winner but wrong score
        elif (self.predicted_result in ["H", "A"] and 
              self.predicted_result == actual_result):
            points += settings.POINTS_CORRECT_WINNER
        
        # Upset bonus: predicted underdog to win and they did
        if self._is_upset_prediction(match):
            points += settings.POINTS_UPSET_BONUS
        
        # Confidence calibration bonus/penalty (simplified Brier score)
        calibration_score = self._calculate_calibration_score(match)
        if calibration_score > 0.7:
            points += 1
        elif calibration_score < 0.3:
            points -= 1
        
        return max(0, points)  # Ensure non-negative
    
    def _is_upset_prediction(self, match) -> bool:
        """
        Check if prediction was an upset (simplified logic).
        
        Args:
            match: Match object
            
        Returns:
            True if upset was predicted and occurred
        """
        # Simplified: assume away team is underdog
        # In production, use team rankings/odds
        if self.predicted_result == "A" and match.result == "A":
            return True
        return False
    
    def _calculate_calibration_score(self, match) -> float:
        """
        Calculate prediction calibration score.
        
        Args:
            match: Match object
            
        Returns:
            Calibration score (0-1)
        """
        # Simplified Brier score calculation
        confidence_decimal = self.confidence / 100.0
        was_correct = self.predicted_result == match.result
        
        if was_correct:
            return confidence_decimal
        else:
            return 1 - confidence_decimal
