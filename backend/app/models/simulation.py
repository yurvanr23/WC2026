"""
Simulation Result Model

Stores tournament simulation outcomes.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime

from app.core.database import Base


class SimulationResult(Base):
    """Tournament simulation results from Monte Carlo analysis"""
    
    __tablename__ = "simulation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Simulation metadata
    simulation_id = Column(String(50), unique=True, nullable=False, index=True)
    iterations = Column(Integer, nullable=False)
    model_version = Column(String(50), nullable=False)
    
    # Results
    winner_probabilities = Column(JSON, nullable=False)  # {team: probability}
    finalist_probabilities = Column(JSON, nullable=False)
    semifinalist_probabilities = Column(JSON, nullable=False)
    stage_reach_probabilities = Column(JSON, nullable=False)  # {team: {stage: prob}}
    
    # Insights
    most_likely_winner = Column(String(100))
    dark_horses = Column(JSON)  # Teams exceeding expectations
    upset_scenarios = Column(JSON)  # Unlikely paths that occurred
    expected_champion = Column(String(100))
    
    # Statistics
    avg_goals_per_match = Column(JSON)  # Per stage
    most_common_final = Column(String(100))  # "Team A vs Team B"
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    execution_time = Column(Integer)  # Milliseconds
    
    def __repr__(self):
        return f"<SimulationResult(id='{self.simulation_id}', iterations={self.iterations}, winner='{self.most_likely_winner}')>"
    
    def get_team_win_probability(self, team: str) -> float:
        """
        Get win probability for a specific team.
        
        Args:
            team: Team name
            
        Returns:
            Win probability (0-1)
        """
        return self.winner_probabilities.get(team, 0.0)
    
    def get_top_contenders(self, n: int = 5) -> list:
        """
        Get top N teams by win probability.
        
        Args:
            n: Number of teams to return
            
        Returns:
            List of (team, probability) tuples
        """
        sorted_teams = sorted(
            self.winner_probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_teams[:n]
    
    def get_stage_probability(self, team: str, stage: str) -> float:
        """
        Get probability of team reaching a specific stage.
        
        Args:
            team: Team name
            stage: Tournament stage
            
        Returns:
            Probability (0-1)
        """
        if not self.stage_reach_probabilities:
            return 0.0
        
        team_probs = self.stage_reach_probabilities.get(team, {})
        return team_probs.get(stage, 0.0)
