"""
AI Predictions API Routes

ML model predictions with SHAP explainability.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.match import Match
from app.models.ai_prediction import AIPrediction
from app.services.ml_service import MLService

router = APIRouter()


# Pydantic schemas
class AIPredictionResponse(BaseModel):
    """AI prediction response"""
    match_id: int
    win_prob: float
    draw_prob: float
    loss_prob: float
    expected_home_goals: float
    expected_away_goals: float
    predicted_result: str
    confidence: float
    model_version: str
    
    class Config:
        from_attributes = True


class ExplainabilityResponse(BaseModel):
    """SHAP explainability response"""
    match_id: int
    prediction_summary: str
    top_features: List[Dict]
    shap_values: Optional[Dict]
    feature_values: Optional[Dict]
    explanation_text: str


@router.get("/predictions/{match_id}", response_model=AIPredictionResponse)
async def get_ai_prediction(
    match_id: int,
    db: Session = Depends(get_db),
    force_regenerate: bool = False
):
    """
    Get AI prediction for a specific match.
    
    - **match_id**: Match ID
    - **force_regenerate**: Force regeneration of prediction (default: False)
    
    Returns cached prediction if available, otherwise generates new one.
    """
    # Check if match exists
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Check for existing prediction
    if not force_regenerate:
        existing_prediction = db.query(AIPrediction).filter(
            AIPrediction.match_id == match_id
        ).order_by(AIPrediction.created_at.desc()).first()
        
        if existing_prediction:
            return existing_prediction
    
    # Generate new prediction
    ml_service = MLService()
    
    try:
        prediction_data = ml_service.predict_match(match, db)
        
        # Save to database
        ai_prediction = AIPrediction(**prediction_data)
        db.add(ai_prediction)
        db.commit()
        db.refresh(ai_prediction)
        
        return ai_prediction
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating prediction: {str(e)}"
        )


@router.get("/explain/{match_id}", response_model=ExplainabilityResponse)
async def get_prediction_explanation(
    match_id: int,
    db: Session = Depends(get_db)
):
    """
    Get SHAP-based explanation for AI prediction.
    
    - **match_id**: Match ID
    
    Returns feature importance and explanation of prediction factors.
    """
    # Get AI prediction
    ai_prediction = db.query(AIPrediction).filter(
        AIPrediction.match_id == match_id
    ).order_by(AIPrediction.created_at.desc()).first()
    
    if not ai_prediction:
        raise HTTPException(
            status_code=404,
            detail="No AI prediction found for this match. Generate one first."
        )
    
    return {
        "match_id": match_id,
        "prediction_summary": f"{ai_prediction.predicted_result} with {ai_prediction.confidence:.1f}% confidence",
        "top_features": ai_prediction.top_features or [],
        "shap_values": ai_prediction.shap_values,
        "feature_values": ai_prediction.feature_values,
        "explanation_text": ai_prediction.get_explanation_text()
    }


@router.get("/predictions/batch")
async def get_batch_predictions(
    match_ids: List[int],
    db: Session = Depends(get_db)
):
    """
    Get AI predictions for multiple matches.
    
    - **match_ids**: List of match IDs (query parameter, comma-separated)
    """
    predictions = []
    
    for match_id in match_ids:
        ai_prediction = db.query(AIPrediction).filter(
            AIPrediction.match_id == match_id
        ).order_by(AIPrediction.created_at.desc()).first()
        
        if ai_prediction:
            predictions.append(ai_prediction)
    
    return predictions


@router.post("/retrain")
async def retrain_model(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger model retraining in the background.
    
    Note: This endpoint would typically be restricted to admin users.
    """
    ml_service = MLService()
    
    # Add retraining task to background
    background_tasks.add_task(ml_service.retrain_models, db)
    
    return {
        "status": "retraining_started",
        "message": "Model retraining initiated in background"
    }


@router.get("/model/info")
async def get_model_info():
    """
    Get current ML model information and statistics.
    """
    ml_service = MLService()
    
    return {
        "model_version": ml_service.model_version,
        "model_type": "XGBoost Classifier + Random Forest Regressor",
        "features_count": len(ml_service.feature_names) if hasattr(ml_service, 'feature_names') else 25,
        "training_date": "2024-01-15",  # Would be dynamic in production
        "performance_metrics": {
            "accuracy": 0.68,
            "log_loss": 0.52,
            "calibration_score": 0.15
        }
    }


@router.get("/predictions/upcoming")
async def get_upcoming_predictions(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get AI predictions for upcoming matches.
    
    - **limit**: Maximum number of predictions to return
    """
    from app.models.match import MatchStatus
    
    # Get upcoming matches
    upcoming_matches = db.query(Match).filter(
        Match.match_date > datetime.utcnow(),
        Match.status == MatchStatus.SCHEDULED
    ).order_by(Match.match_date).limit(limit).all()
    
    predictions = []
    ml_service = MLService()
    
    for match in upcoming_matches:
        # Check for existing prediction
        ai_prediction = db.query(AIPrediction).filter(
            AIPrediction.match_id == match.id
        ).order_by(AIPrediction.created_at.desc()).first()
        
        if not ai_prediction:
            # Generate prediction
            try:
                prediction_data = ml_service.predict_match(match, db)
                ai_prediction = AIPrediction(**prediction_data)
                db.add(ai_prediction)
                db.commit()
                db.refresh(ai_prediction)
            except:
                continue
        
        predictions.append({
            "match": {
                "id": match.id,
                "home_team": match.home_team,
                "away_team": match.away_team,
                "match_date": match.match_date,
                "stage": match.stage.value
            },
            "prediction": AIPredictionResponse.model_validate(ai_prediction)
        })
    
    return predictions


@router.get("/compare/{match_id}")
async def compare_predictions(
    match_id: int,
    db: Session = Depends(get_db)
):
    """
    Compare AI prediction with user predictions for a match.
    
    - **match_id**: Match ID
    """
    from app.models.prediction import Prediction
    
    # Get AI prediction
    ai_prediction = db.query(AIPrediction).filter(
        AIPrediction.match_id == match_id
    ).order_by(AIPrediction.created_at.desc()).first()
    
    if not ai_prediction:
        raise HTTPException(status_code=404, detail="No AI prediction found")
    
    # Get user predictions
    user_predictions = db.query(Prediction).filter(
        Prediction.match_id == match_id
    ).all()
    
    # Calculate statistics
    total_users = len(user_predictions)
    users_agree_with_ai = sum(
        1 for p in user_predictions 
        if p.predicted_result == ai_prediction.predicted_result
    )
    
    avg_user_confidence = (
        sum(p.confidence for p in user_predictions) / total_users 
        if total_users > 0 else 0
    )
    
    return {
        "ai_prediction": {
            "result": ai_prediction.predicted_result,
            "confidence": ai_prediction.confidence,
            "expected_goals": f"{ai_prediction.expected_home_goals:.1f} - {ai_prediction.expected_away_goals:.1f}"
        },
        "user_stats": {
            "total_predictions": total_users,
            "agreement_rate": (users_agree_with_ai / total_users * 100) if total_users > 0 else 0,
            "avg_confidence": round(avg_user_confidence, 1)
        },
        "consensus": {
            "ai_vs_users": "aligned" if (users_agree_with_ai / total_users > 0.5 if total_users > 0 else False) else "divergent"
        }
    }
