"""
Tournament Simulation API Routes

Monte Carlo tournament simulation.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List
import uuid

from app.core.database import get_db
from app.services.simulation_service import SimulationService
from app.models.simulation import SimulationResult

router = APIRouter()


class SimulationRequest(BaseModel):
    """Simulation request"""
    iterations: int = 10000
    use_latest_model: bool = True


class SimulationResponse(BaseModel):
    """Simulation response"""
    simulation_id: str
    status: str
    message: str


@router.post("/tournament", response_model=SimulationResponse)
async def run_tournament_simulation(
    request: SimulationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Run Monte Carlo tournament simulation.
    
    - **iterations**: Number of simulations (default: 10000)
    - **use_latest_model**: Use latest ML model (default: True)
    
    Runs simulation in background and returns simulation ID.
    """
    simulation_id = str(uuid.uuid4())
    
    simulation_service = SimulationService()
    
    # Run simulation in background
    background_tasks.add_task(
        simulation_service.run_tournament_simulation,
        simulation_id,
        request.iterations,
        db
    )
    
    return {
        "simulation_id": simulation_id,
        "status": "running",
        "message": f"Simulation started with {request.iterations} iterations"
    }


@router.get("/results/{simulation_id}")
async def get_simulation_results(
    simulation_id: str,
    db: Session = Depends(get_db)
):
    """
    Get results from a completed simulation.
    
    - **simulation_id**: Simulation ID from run request
    """
    result = db.query(SimulationResult).filter(
        SimulationResult.simulation_id == simulation_id
    ).first()
    
    if not result:
        return {
            "status": "running",
            "message": "Simulation in progress or not found"
        }
    
    return {
        "status": "completed",
        "simulation_id": result.simulation_id,
        "iterations": result.iterations,
        "winner_probabilities": result.winner_probabilities,
        "finalist_probabilities": result.finalist_probabilities,
        "most_likely_winner": result.most_likely_winner,
        "dark_horses": result.dark_horses,
        "execution_time": result.execution_time
    }


@router.get("/probabilities")
async def get_winner_probabilities(db: Session = Depends(get_db)):
    """
    Get latest tournament winner probabilities.
    
    Returns most recent simulation results.
    """
    latest = db.query(SimulationResult).order_by(
        SimulationResult.created_at.desc()
    ).first()
    
    if not latest:
        raise HTTPException(
            status_code=404,
            detail="No simulation results available. Run a simulation first."
        )
    
    return {
        "winner_probabilities": latest.winner_probabilities,
        "top_5": latest.get_top_contenders(5),
        "simulation_date": latest.created_at
    }


@router.get("/team/{team_name}")
async def get_team_probabilities(
    team_name: str,
    db: Session = Depends(get_db)
):
    """
    Get probabilities for a specific team across all stages.
    
    - **team_name**: Team name
    """
    latest = db.query(SimulationResult).order_by(
        SimulationResult.created_at.desc()
    ).first()
    
    if not latest:
        raise HTTPException(status_code=404, detail="No simulation results available")
    
    win_prob = latest.get_team_win_probability(team_name)
    
    if win_prob == 0:
        raise HTTPException(status_code=404, detail="Team not found in simulation")
    
    return {
        "team": team_name,
        "win_probability": win_prob,
        "finalist_probability": latest.finalist_probabilities.get(team_name, 0),
        "stage_probabilities": latest.stage_reach_probabilities.get(team_name, {})
    }
