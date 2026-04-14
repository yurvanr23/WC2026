"""
Tournament Simulation Service

Monte Carlo simulation for tournament outcomes.
"""

import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict
from datetime import datetime
from sqlalchemy.orm import Session
import time

from app.models.match import Match, TournamentStage
from app.models.simulation import SimulationResult
from app.services.ml_service import MLService


class SimulationService:
    """Service for tournament simulation"""
    
    def __init__(self):
        self.ml_service = MLService()
    
    def run_tournament_simulation(
        self,
        simulation_id: str,
        iterations: int,
        db: Session
    ):
        """
        Run Monte Carlo tournament simulation.
        
        Args:
            simulation_id: Unique simulation identifier
            iterations: Number of simulations to run
            db: Database session
        """
        start_time = time.time()
        
        # Initialize result counters
        winner_counts = defaultdict(int)
        finalist_counts = defaultdict(int)
        semifinalist_counts = defaultdict(int)
        stage_reach_counts = defaultdict(lambda: defaultdict(int))
        
        # Get tournament structure
        teams = self._get_tournament_teams(db)
        
        # Run simulations
        for i in range(iterations):
            tournament_result = self._simulate_single_tournament(teams, db)
            
            # Record results
            winner_counts[tournament_result['winner']] += 1
            
            for finalist in tournament_result['finalists']:
                finalist_counts[finalist] += 1
            
            for semifinalist in tournament_result['semifinalists']:
                semifinalist_counts[semifinalist] += 1
            
            # Track stage reach for each team
            for team, stage in tournament_result['team_stages'].items():
                stage_reach_counts[team][stage] += 1
        
        # Calculate probabilities
        winner_probs = {
            team: count / iterations 
            for team, count in winner_counts.items()
        }
        
        finalist_probs = {
            team: count / iterations 
            for team, count in finalist_counts.items()
        }
        
        semifinalist_probs = {
            team: count / iterations 
            for team, count in semifinalist_counts.items()
        }
        
        stage_reach_probs = {
            team: {
                stage: count / iterations 
                for stage, count in stages.items()
            }
            for team, stages in stage_reach_counts.items()
        }
        
        # Identify insights
        most_likely_winner = max(winner_probs, key=winner_probs.get)
        dark_horses = self._identify_dark_horses(winner_probs, teams)
        
        # Calculate execution time
        execution_time = int((time.time() - start_time) * 1000)
        
        # Save results
        simulation = SimulationResult(
            simulation_id=simulation_id,
            iterations=iterations,
            model_version=self.ml_service.model_version,
            winner_probabilities=winner_probs,
            finalist_probabilities=finalist_probs,
            semifinalist_probabilities=semifinalist_probs,
            stage_reach_probabilities=stage_reach_probs,
            most_likely_winner=most_likely_winner,
            dark_horses=dark_horses,
            expected_champion=most_likely_winner,
            execution_time=execution_time
        )
        
        db.add(simulation)
        db.commit()
        
        print(f"Simulation {simulation_id} completed in {execution_time}ms")
    
    def _simulate_single_tournament(self, teams: List[str], db: Session) -> Dict:
        """
        Simulate a single tournament run.
        
        Args:
            teams: List of team names
            db: Database session
            
        Returns:
            Dictionary with tournament results
        """
        team_stages = {team: 'group' for team in teams}
        
        # Group stage
        knockout_teams = self._simulate_group_stage(teams)
        
        # Update stages
        for team in knockout_teams:
            team_stages[team] = 'round_16'
        
        # Round of 16
        quarter_teams = self._simulate_knockout_round(knockout_teams, 'round_16')
        for team in quarter_teams:
            team_stages[team] = 'quarter'
        
        # Quarter finals
        semi_teams = self._simulate_knockout_round(quarter_teams, 'quarter')
        for team in semi_teams:
            team_stages[team] = 'semi'
        
        # Semi finals
        final_teams = self._simulate_knockout_round(semi_teams, 'semi')
        for team in final_teams:
            team_stages[team] = 'final'
        
        # Final
        winner = self._simulate_match(final_teams[0], final_teams[1])
        team_stages[winner] = 'winner'
        
        return {
            'winner': winner,
            'finalists': final_teams,
            'semifinalists': semi_teams,
            'team_stages': team_stages
        }
    
    def _simulate_group_stage(self, teams: List[str]) -> List[str]:
        """
        Simulate group stage.
        
        Args:
            teams: All teams
            
        Returns:
            Teams advancing to knockout (top 2 from each group)
        """
        # Simplified: assume 8 groups of 4 teams
        # Top 2 from each group advance
        
        # Mock group assignment
        np.random.shuffle(teams)
        groups = [teams[i:i+4] for i in range(0, min(32, len(teams)), 4)]
        
        advancing = []
        for group in groups:
            # Simulate group matches and get top 2
            # Simplified: use FIFA rank as proxy
            sorted_group = sorted(
                group,
                key=lambda t: self.ml_service._get_fifa_rank(t)
            )
            advancing.extend(sorted_group[:2])
        
        return advancing[:16]  # Return 16 teams for knockout
    
    def _simulate_knockout_round(
        self,
        teams: List[str],
        stage: str
    ) -> List[str]:
        """
        Simulate a knockout round.
        
        Args:
            teams: Teams in this round
            stage: Round name
            
        Returns:
            Winning teams
        """
        winners = []
        
        # Pair teams and simulate matches
        for i in range(0, len(teams), 2):
            if i + 1 < len(teams):
                winner = self._simulate_match(teams[i], teams[i + 1])
                winners.append(winner)
        
        return winners
    
    def _simulate_match(self, team1: str, team2: str) -> str:
        """
        Simulate a single match outcome.
        
        Args:
            team1: First team
            team2: Second team
            
        Returns:
            Winning team
        """
        # Get team strengths (simplified)
        rank1 = self.ml_service._get_fifa_rank(team1)
        rank2 = self.ml_service._get_fifa_rank(team2)
        
        # Lower rank = better team
        # Convert to win probability
        prob_team1 = 1 / (1 + np.exp(0.05 * (rank1 - rank2)))
        
        # Sample outcome
        if np.random.random() < prob_team1:
            return team1
        else:
            return team2
    
    def _get_tournament_teams(self, db: Session) -> List[str]:
        """
        Get list of teams participating in tournament.
        
        Args:
            db: Database session
            
        Returns:
            List of team names
        """
        # Get unique teams from matches
        matches = db.query(Match).all()
        teams = set()
        
        for match in matches:
            teams.add(match.home_team)
            teams.add(match.away_team)
        
        # If no matches, use default teams
        if not teams:
            teams = {
                'Argentina', 'France', 'Brazil', 'England',
                'Belgium', 'Netherlands', 'Portugal', 'Spain',
                'Italy', 'Germany', 'Uruguay', 'Croatia',
                'Denmark', 'Mexico', 'USA', 'Switzerland',
                'Colombia', 'Senegal', 'Wales', 'Iran',
                'Serbia', 'Morocco', 'Japan', 'South Korea',
                'Ecuador', 'Qatar', 'Saudi Arabia', 'Tunisia',
                'Canada', 'Ghana', 'Cameroon', 'Poland'
            }
        
        return list(teams)
    
    def _identify_dark_horses(
        self,
        winner_probs: Dict[str, float],
        teams: List[str]
    ) -> List[Dict]:
        """
        Identify dark horse teams (exceeding expectations).
        
        Args:
            winner_probs: Winner probabilities
            teams: All teams
            
        Returns:
            List of dark horse teams with details
        """
        dark_horses = []
        
        for team, prob in winner_probs.items():
            rank = self.ml_service._get_fifa_rank(team)
            
            # Dark horse: lower ranked team with decent win probability
            if rank > 15 and prob > 0.02:
                dark_horses.append({
                    'team': team,
                    'win_probability': prob,
                    'fifa_rank': rank,
                    'surprise_factor': prob * rank / 100
                })
        
        # Sort by surprise factor
        dark_horses.sort(key=lambda x: x['surprise_factor'], reverse=True)
        
        return dark_horses[:5]  # Top 5 dark horses
