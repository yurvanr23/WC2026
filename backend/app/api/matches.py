"""
Matches API Routes

Match listings, details, and filtering.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.match import Match, MatchStatus, TournamentStage

router = APIRouter()


# Pydantic schemas
class MatchResponse(BaseModel):
    """Match data response"""
    id: int
    home_team: str
    away_team: str
    match_date: datetime
    venue: Optional[str]
    stage: str
    group_name: Optional[str]
    home_score: Optional[int]
    away_score: Optional[int]
    status: str
    result: Optional[str]
    
    class Config:
        from_attributes = True


class MatchListResponse(BaseModel):
    """Paginated match list response"""
    matches: List[MatchResponse]
    total: int
    page: int
    page_size: int


@router.get("", response_model=MatchListResponse)
async def get_matches(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[MatchStatus] = None,
    stage: Optional[TournamentStage] = None,
    team: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of matches with optional filtering.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **status**: Filter by match status (scheduled/live/finished)
    - **stage**: Filter by tournament stage
    - **team**: Filter matches involving specific team
    """
    query = db.query(Match)
    
    # Apply filters
    if status:
        query = query.filter(Match.status == status)
    
    if stage:
        query = query.filter(Match.stage == stage)
    
    if team:
        query = query.filter(
            (Match.home_team.ilike(f"%{team}%")) | 
            (Match.away_team.ilike(f"%{team}%"))
        )
    
    # Order by match date
    query = query.order_by(Match.match_date)
    
    # Get total count
    total = query.count()
    
    # Pagination
    offset = (page - 1) * page_size
    matches = query.offset(offset).limit(page_size).all()
    
    return {
        "matches": matches,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/upcoming", response_model=List[MatchResponse])
async def get_upcoming_matches(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get upcoming matches.
    
    - **limit**: Maximum number of matches to return (default: 10)
    """
    now = datetime.utcnow()
    
    matches = db.query(Match).filter(
        Match.match_date > now,
        Match.status == MatchStatus.SCHEDULED
    ).order_by(Match.match_date).limit(limit).all()
    
    return matches


@router.get("/live", response_model=List[MatchResponse])
async def get_live_matches(db: Session = Depends(get_db)):
    """
    Get currently live matches.
    """
    matches = db.query(Match).filter(
        Match.status == MatchStatus.LIVE
    ).order_by(Match.match_date.desc()).all()
    
    return matches


@router.get("/recent", response_model=List[MatchResponse])
async def get_recent_matches(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get recently finished matches.
    
    - **limit**: Maximum number of matches to return (default: 10)
    """
    matches = db.query(Match).filter(
        Match.status == MatchStatus.FINISHED
    ).order_by(Match.match_date.desc()).limit(limit).all()
    
    return matches


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific match.
    
    - **match_id**: Match ID
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    return match


@router.get("/stage/{stage}", response_model=List[MatchResponse])
async def get_matches_by_stage(
    stage: TournamentStage,
    db: Session = Depends(get_db)
):
    """
    Get all matches from a specific tournament stage.
    
    - **stage**: Tournament stage (group/round_16/quarter/semi/final)
    """
    matches = db.query(Match).filter(
        Match.stage == stage
    ).order_by(Match.match_date).all()
    
    return matches


@router.get("/team/{team_name}", response_model=List[MatchResponse])
async def get_team_matches(
    team_name: str,
    db: Session = Depends(get_db)
):
    """
    Get all matches for a specific team.
    
    - **team_name**: Team name
    """
    matches = db.query(Match).filter(
        (Match.home_team.ilike(f"%{team_name}%")) | 
        (Match.away_team.ilike(f"%{team_name}%"))
    ).order_by(Match.match_date).all()
    
    if not matches:
        raise HTTPException(status_code=404, detail="No matches found for team")
    
    return matches
