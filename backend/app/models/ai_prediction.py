"""
AI Prediction Model

Stores ML model predictions and explanations.
"""

from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class AIPrediction(Base):
    """AI-generated match predictions with explainability"""
    
    __tablename__ = "ai_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Probability predictions (must sum to ~1.0)
    win_prob = Column(Float, nullable=False)  # Home team win probability
    draw_prob = Column(Float, nullable=False)
    loss_prob = Column(Float, nullable=False)  # Away team win probability
    
    # Expected goals
    expected_home_goals = Column(Float, nullable=False)
    expected_away_goals = Column(Float, nullable=False)
    
    # Confidence intervals
    home_goals_lower = Column(Float)  # 95% CI lower bound
    home_goals_upper = Column(Float)  # 95% CI upper bound
    away_goals_lower = Column(Float)
    away_goals_upper = Column(Float)
    
    # Model metadata
    model_version = Column(String(50), nullable=False)
    model_type = Column(String(50), default="xgboost_classifier")
    
    # Explainability data (SHAP values)
    shap_values = Column(JSON)  # Stores SHAP feature importance
    feature_values = Column(JSON)  # Stores feature values used
    top_features = Column(JSON)  # Top 5 influential features
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    match = relationship("Match", back_populates="ai_predictions")
    
    def __repr__(self):
        return f"<AIPrediction(match={self.match_id}, win={self.win_prob:.2f}, draw={self.draw_prob:.2f}, loss={self.loss_prob:.2f})>"
    
    @property
    def predicted_result(self) -> str:
        """Get most likely result based on probabilities"""
        probs = {
            "H": self.win_prob,
            "D": self.draw_prob,
            "A": self.loss_prob
        }
        return max(probs, key=probs.get)
    
    @property
    def confidence(self) -> float:
        """Get confidence level (max probability)"""
        return max(self.win_prob, self.draw_prob, self.loss_prob) * 100
    
    @property
    def expected_total_goals(self) -> float:
        """Get expected total goals"""
        return self.expected_home_goals + self.expected_away_goals
    
    @property
    def probability_entropy(self) -> float:
        """
        Calculate entropy of probability distribution.
        Higher entropy = more uncertainty.
        """
        import math
        probs = [self.win_prob, self.draw_prob, self.loss_prob]
        entropy = -sum(p * math.log(p) if p > 0 else 0 for p in probs)
        return entropy
    
    def get_top_features_summary(self, n: int = 5) -> list:
        """
        Get top N features influencing prediction.
        
        Args:
            n: Number of top features to return
            
        Returns:
            List of (feature_name, importance) tuples
        """
        if not self.top_features:
            return []
        
        return self.top_features[:n]
    
    def get_explanation_text(self) -> str:
        """
        Generate human-readable explanation of prediction.
        
        Returns:
            Explanation string
        """
        result_map = {
            "H": "home team win",
            "D": "draw",
            "A": "away team win"
        }
        
        predicted = result_map[self.predicted_result]
        confidence = self.confidence
        
        explanation = f"The model predicts a {predicted} with {confidence:.1f}% confidence. "
        explanation += f"Expected score: {self.expected_home_goals:.1f} - {self.expected_away_goals:.1f}. "
        
        if self.top_features and len(self.top_features) > 0:
            top_feature = self.top_features[0]
            explanation += f"Key factor: {top_feature.get('name', 'team form')}."
        
        return explanation
