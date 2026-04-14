"""
Machine Learning Service

Handles ML model predictions, feature engineering, and SHAP explanations.
"""

import numpy as np
import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.match import Match


class MLService:
    """Service for ML model operations"""
    
    def __init__(self):
        self.model_version = settings.MODEL_VERSION
        self.feature_names = self._get_feature_names()
        
        # In production, load actual trained models
        # self.classifier = joblib.load(f"{settings.MODEL_PATH}/classifier_{self.model_version}.pkl")
        # self.regressor = joblib.load(f"{settings.MODEL_PATH}/regressor_{self.model_version}.pkl")
        
    def _get_feature_names(self) -> List[str]:
        """Get list of feature names used by the model"""
        return [
            'team_form_home', 'team_form_away',
            'goal_diff_home', 'goal_diff_away',
            'goals_scored_home_avg', 'goals_scored_away_avg',
            'goals_conceded_home_avg', 'goals_conceded_away_avg',
            'fifa_rank_home', 'fifa_rank_away',
            'rank_difference',
            'home_advantage',
            'h2h_wins_home', 'h2h_wins_away', 'h2h_draws',
            'squad_age_home', 'squad_age_away',
            'squad_experience_home', 'squad_experience_away',
            'recent_goals_home', 'recent_goals_away',
            'clean_sheets_home', 'clean_sheets_away',
            'tournament_stage_encoded',
            'days_since_last_match_home', 'days_since_last_match_away'
        ]
    
    def predict_match(self, match: Match, db: Session) -> Dict:
        """
        Generate ML prediction for a match.
        
        Args:
            match: Match object
            db: Database session
            
        Returns:
            Dictionary with prediction data
        """
        # Extract features
        features = self._extract_features(match, db)
        
        # Generate predictions (mock for now - replace with actual model)
        win_prob, draw_prob, loss_prob = self._predict_probabilities(features)
        expected_home_goals, expected_away_goals = self._predict_scoreline(features)
        
        # Generate SHAP explanations
        shap_data = self._generate_shap_explanation(features) if settings.SHAP_ENABLED else {}
        
        return {
            "match_id": match.id,
            "win_prob": win_prob,
            "draw_prob": draw_prob,
            "loss_prob": loss_prob,
            "expected_home_goals": expected_home_goals,
            "expected_away_goals": expected_away_goals,
            "home_goals_lower": max(0, expected_home_goals - 0.8),
            "home_goals_upper": expected_home_goals + 0.8,
            "away_goals_lower": max(0, expected_away_goals - 0.8),
            "away_goals_upper": expected_away_goals + 0.8,
            "model_version": self.model_version,
            "model_type": "xgboost_classifier",
            "shap_values": shap_data.get("shap_values"),
            "feature_values": shap_data.get("feature_values"),
            "top_features": shap_data.get("top_features", [])
        }
    
    def _extract_features(self, match: Match, db: Session) -> Dict:
        """
        Extract features for a match.
        
        Args:
            match: Match object
            db: Database session
            
        Returns:
            Dictionary of feature values
        """
        # Mock feature extraction - in production, query historical data
        features = {}
        
        # Team form (last 5 matches)
        features['team_form_home'] = self._calculate_team_form(match.home_team, db)
        features['team_form_away'] = self._calculate_team_form(match.away_team, db)
        
        # Goal statistics
        features['goal_diff_home'] = self._get_goal_difference(match.home_team, db)
        features['goal_diff_away'] = self._get_goal_difference(match.away_team, db)
        features['goals_scored_home_avg'] = self._get_avg_goals_scored(match.home_team, db)
        features['goals_scored_away_avg'] = self._get_avg_goals_scored(match.away_team, db)
        features['goals_conceded_home_avg'] = self._get_avg_goals_conceded(match.home_team, db)
        features['goals_conceded_away_avg'] = self._get_avg_goals_conceded(match.away_team, db)
        
        # FIFA rankings (mock)
        features['fifa_rank_home'] = self._get_fifa_rank(match.home_team)
        features['fifa_rank_away'] = self._get_fifa_rank(match.away_team)
        features['rank_difference'] = features['fifa_rank_home'] - features['fifa_rank_away']
        
        # Home advantage
        features['home_advantage'] = 1  # Binary: 1 if playing in host country
        
        # Head-to-head
        h2h = self._get_head_to_head(match.home_team, match.away_team, db)
        features['h2h_wins_home'] = h2h['wins_home']
        features['h2h_wins_away'] = h2h['wins_away']
        features['h2h_draws'] = h2h['draws']
        
        # Squad metrics (mock)
        features['squad_age_home'] = 26.5
        features['squad_age_away'] = 27.2
        features['squad_experience_home'] = 45.0
        features['squad_experience_away'] = 42.0
        
        # Recent performance
        features['recent_goals_home'] = self._get_recent_goals(match.home_team, db)
        features['recent_goals_away'] = self._get_recent_goals(match.away_team, db)
        features['clean_sheets_home'] = self._get_clean_sheets(match.home_team, db)
        features['clean_sheets_away'] = self._get_clean_sheets(match.away_team, db)
        
        # Tournament stage encoding
        stage_encoding = {
            'group': 0, 'round_16': 1, 'quarter': 2,
            'semi': 3, 'third_place': 4, 'final': 5
        }
        features['tournament_stage_encoded'] = stage_encoding.get(match.stage.value, 0)
        
        # Days since last match
        features['days_since_last_match_home'] = 7
        features['days_since_last_match_away'] = 6
        
        return features
    
    def _predict_probabilities(self, features: Dict) -> tuple:
        """
        Predict match outcome probabilities.
        
        Args:
            features: Feature dictionary
            
        Returns:
            Tuple of (win_prob, draw_prob, loss_prob)
        """
        # Mock prediction - replace with actual model
        # In production: self.classifier.predict_proba(feature_array)
        
        # Simple heuristic based on rank difference
        rank_diff = features.get('rank_difference', 0)
        form_diff = features['team_form_home'] - features['team_form_away']
        
        # Normalize to probabilities
        advantage = (rank_diff * -0.01) + (form_diff * 0.1) + (features['home_advantage'] * 0.1)
        
        # Calculate probabilities
        win_prob = max(0.1, min(0.8, 0.4 + advantage))
        loss_prob = max(0.1, min(0.8, 0.4 - advantage))
        draw_prob = max(0.1, 1.0 - win_prob - loss_prob)
        
        # Normalize
        total = win_prob + draw_prob + loss_prob
        win_prob /= total
        draw_prob /= total
        loss_prob /= total
        
        return round(win_prob, 3), round(draw_prob, 3), round(loss_prob, 3)
    
    def _predict_scoreline(self, features: Dict) -> tuple:
        """
        Predict expected goals for both teams.
        
        Args:
            features: Feature dictionary
            
        Returns:
            Tuple of (expected_home_goals, expected_away_goals)
        """
        # Mock prediction - replace with actual regressor
        # In production: self.regressor.predict(feature_array)
        
        base_home = features.get('goals_scored_home_avg', 1.5)
        base_away = features.get('goals_scored_away_avg', 1.3)
        
        # Adjust for form and advantage
        home_boost = features['team_form_home'] * 0.2 + features['home_advantage'] * 0.3
        away_boost = features['team_form_away'] * 0.2
        
        expected_home = max(0.5, base_home + home_boost)
        expected_away = max(0.5, base_away + away_boost)
        
        return round(expected_home, 2), round(expected_away, 2)
    
    def _generate_shap_explanation(self, features: Dict) -> Dict:
        """
        Generate SHAP-based explanation.
        
        Args:
            features: Feature dictionary
            
        Returns:
            Dictionary with SHAP values and top features
        """
        # Mock SHAP values - replace with actual SHAP computation
        # In production: shap.TreeExplainer(model).shap_values(features)
        
        # Generate mock SHAP values
        shap_values = {}
        for feature_name, value in features.items():
            # Mock importance based on feature type
            if 'form' in feature_name:
                importance = np.random.uniform(0.1, 0.3)
            elif 'rank' in feature_name:
                importance = np.random.uniform(0.05, 0.25)
            else:
                importance = np.random.uniform(0.01, 0.15)
            
            shap_values[feature_name] = round(importance, 3)
        
        # Get top features
        sorted_features = sorted(
            shap_values.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        top_features = [
            {
                "name": feat[0].replace('_', ' ').title(),
                "value": features.get(feat[0]),
                "importance": abs(feat[1])
            }
            for feat in sorted_features[:5]
        ]
        
        return {
            "shap_values": shap_values,
            "feature_values": features,
            "top_features": top_features
        }
    
    # Helper methods for feature extraction
    
    def _calculate_team_form(self, team: str, db: Session, n_matches: int = 5) -> float:
        """Calculate team form based on recent matches"""
        # Mock - query last N matches and calculate points per game
        return np.random.uniform(1.0, 2.5)
    
    def _get_goal_difference(self, team: str, db: Session) -> int:
        """Get goal difference"""
        return np.random.randint(-5, 10)
    
    def _get_avg_goals_scored(self, team: str, db: Session) -> float:
        """Get average goals scored"""
        return round(np.random.uniform(1.0, 2.5), 2)
    
    def _get_avg_goals_conceded(self, team: str, db: Session) -> float:
        """Get average goals conceded"""
        return round(np.random.uniform(0.5, 1.8), 2)
    
    def _get_fifa_rank(self, team: str) -> int:
        """Get FIFA ranking"""
        # Mock FIFA rankings
        rankings = {
            'Argentina': 1, 'France': 2, 'Brazil': 3, 'England': 4,
            'Belgium': 5, 'Netherlands': 6, 'Portugal': 7, 'Spain': 8,
            'Italy': 9, 'Germany': 10
        }
        return rankings.get(team, np.random.randint(10, 50))
    
    def _get_head_to_head(self, team1: str, team2: str, db: Session) -> Dict:
        """Get head-to-head record"""
        return {
            'wins_home': np.random.randint(0, 5),
            'wins_away': np.random.randint(0, 5),
            'draws': np.random.randint(0, 3)
        }
    
    def _get_recent_goals(self, team: str, db: Session) -> int:
        """Get recent goals scored (last 3 matches)"""
        return np.random.randint(2, 8)
    
    def _get_clean_sheets(self, team: str, db: Session) -> int:
        """Get clean sheets in recent matches"""
        return np.random.randint(0, 3)
    
    def retrain_models(self, db: Session):
        """
        Retrain ML models with latest data.
        
        Args:
            db: Database session
        """
        # This would implement the full retraining pipeline
        # 1. Extract training data
        # 2. Feature engineering
        # 3. Train models
        # 4. Evaluate performance
        # 5. Save new model version
        
        print(f"Retraining models... (placeholder)")
        pass
