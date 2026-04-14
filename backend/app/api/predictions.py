"""
Predictions API Routes

User prediction submission and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.match import Match, MatchStatus
from app.models.prediction import Prediction

router = APIRouter()


# Pydantic schemas
class PredictionCreate(BaseModel):
    """Create prediction request"""
    match_id: int
    predicted_home_score: int = Field(..., ge=0, le=20)
    predicted_away_score: int = Field(..., ge=0, le=20)
    confidence: int = Field(..., ge=0, le=100)


class PredictionUpdate(BaseModel):
    """Update prediction request"""
    predicted_home_score: int = Field(..., ge=0, le=20)
    predicted_away_score: int = Field(..., ge=0, le=20)
    confidence: int = Field(..., ge=0, le=100)


class PredictionResponse(BaseModel):
    """Prediction response"""
    id: int
    match_id: int
    user_id: int
    predicted_home_score: int
    predicted_away_score: int
    confidence: int
    points_earned: int
    is_scored: int
    predicted_result: str
    created_at: datetime
    
    # Include match details
    match: dict
    
    class Config:
        from_attributes = True


@router.post("", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    prediction_data: PredictionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a prediction for a match.
    
    - **match_id**: ID of the match
    - **predicted_home_score**: Predicted home team score
    - **predicted_away_score**: Predicted away team score
    - **confidence**: Confidence level (0-100)
    
    Requires authentication.
    """
    # Check if match exists
    match = db.query(Match).filter(Match.id == prediction_data.match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Check if match has already started
    if match.match_date <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot predict for matches that have already started"
        )
    
    # Check if prediction already exists
    existing_prediction = db.query(Prediction).filter(
        Prediction.user_id == current_user.id,
        Prediction.match_id == prediction_data.match_id
    ).first()
    
    if existing_prediction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prediction already exists for this match. Use PUT to update."
        )
    
    # Create prediction
    prediction = Prediction(
        user_id=current_user.id,
        match_id=prediction_data.match_id,
        predicted_home_score=prediction_data.predicted_home_score,
        predicted_away_score=prediction_data.predicted_away_score,
        confidence=prediction_data.confidence
    )
    
    db.add(prediction)
    
    # Update user prediction count
    current_user.predictions_count += 1
    
    db.commit()
    db.refresh(prediction)
    
    # Prepare response with match details
    response = PredictionResponse.model_validate(prediction)
    response.match = {
        "home_team": match.home_team,
        "away_team": match.away_team,
        "match_date": match.match_date,
        "stage": match.stage.value
    }
    
    return response


@router.get("/user", response_model=List[PredictionResponse])
async def get_user_predictions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    scored_only: bool = Query(False)
):
    """
    Get all predictions for the current user.
    
    - **scored_only**: Only return predictions that have been scored
    
    Requires authentication.
    """
    query = db.query(Prediction).filter(Prediction.user_id == current_user.id)
    
    if scored_only:
        query = query.filter(Prediction.is_scored == True)
    
    predictions = query.order_by(Prediction.created_at.desc()).all()
    
    # Enhance with match details
    result = []
    for pred in predictions:
        pred_response = PredictionResponse.model_validate(pred)
        pred_response.match = {
            "home_team": pred.match.home_team,
            "away_team": pred.match.away_team,
            "match_date": pred.match.match_date,
            "stage": pred.match.stage.value,
            "status": pred.match.status.value,
            "home_score": pred.match.home_score,
            "away_score": pred.match.away_score
        }
        result.append(pred_response)
    
    return result


@router.get("/match/{match_id}")
async def get_match_predictions(
    match_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get predictions for a specific match (public view).
    
    - **match_id**: Match ID
    - **limit**: Maximum number of predictions to return
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    predictions = db.query(Prediction).filter(
        Prediction.match_id == match_id
    ).limit(limit).all()
    
    # Aggregate statistics
    total_predictions = len(predictions)
    home_win_predictions = sum(1 for p in predictions if p.predicted_result == "H")
    draw_predictions = sum(1 for p in predictions if p.predicted_result == "D")
    away_win_predictions = sum(1 for p in predictions if p.predicted_result == "A")
    
    avg_confidence = sum(p.confidence for p in predictions) / total_predictions if total_predictions > 0 else 0
    
    return {
        "match_id": match_id,
        "total_predictions": total_predictions,
        "result_distribution": {
            "home_win": home_win_predictions,
            "draw": draw_predictions,
            "away_win": away_win_predictions
        },
        "average_confidence": round(avg_confidence, 1)
    }


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific prediction.
    
    - **prediction_id**: Prediction ID
    
    Requires authentication. Users can only view their own predictions.
    """
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id
    ).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    pred_response = PredictionResponse.model_validate(prediction)
    pred_response.match = {
        "home_team": prediction.match.home_team,
        "away_team": prediction.match.away_team,
        "match_date": prediction.match.match_date,
        "stage": prediction.match.stage.value
    }
    
    return pred_response


@router.put("/{prediction_id}", response_model=PredictionResponse)
async def update_prediction(
    prediction_id: int,
    update_data: PredictionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing prediction.
    
    - **prediction_id**: Prediction ID
    - **predicted_home_score**: New predicted home score
    - **predicted_away_score**: New predicted away score
    - **confidence**: New confidence level
    
    Can only update before match starts. Requires authentication.
    """
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id
    ).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    # Check if match has started
    if prediction.match.match_date <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update prediction after match has started"
        )
    
    # Update prediction
    prediction.predicted_home_score = update_data.predicted_home_score
    prediction.predicted_away_score = update_data.predicted_away_score
    prediction.confidence = update_data.confidence
    prediction.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(prediction)
    
    pred_response = PredictionResponse.model_validate(prediction)
    pred_response.match = {
        "home_team": prediction.match.home_team,
        "away_team": prediction.match.away_team,
        "match_date": prediction.match.match_date,
        "stage": prediction.match.stage.value
    }
    
    return pred_response


@router.delete("/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prediction(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a prediction.
    
    - **prediction_id**: Prediction ID
    
    Can only delete before match starts. Requires authentication.
    """
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id
    ).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    # Check if match has started
    if prediction.match.match_date <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete prediction after match has started"
        )
    
    db.delete(prediction)
    current_user.predictions_count -= 1
    db.commit()
    
    return None
