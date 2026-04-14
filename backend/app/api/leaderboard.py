"""
Leaderboard API Routes

Global and league-based leaderboards with Redis caching.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel, Field
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.league import League, LeagueMembership
from app.services.leaderboard_service import LeaderboardService

router = APIRouter()


# Pydantic schemas
class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    rank: int
    user_id: int
    username: str
    total_points: int
    predictions_count: int
    accuracy: float
    exact_scores: int


class LeagueCreate(BaseModel):
    """Create league request"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    max_members: int = Field(50, ge=2, le=200)
    is_private: bool = True


class LeagueResponse(BaseModel):
    """League details response"""
    id: int
    name: str
    description: Optional[str]
    invite_code: str
    owner_id: int
    member_count: int
    max_members: int
    is_private: bool
    
    class Config:
        from_attributes = True


@router.get("/global")
async def get_global_leaderboard(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get global leaderboard.
    
    - **page**: Page number
    - **page_size**: Items per page
    
    Results are cached in Redis for performance.
    """
    leaderboard_service = LeaderboardService()
    
    # Try to get from cache
    cached_result = leaderboard_service.get_global_leaderboard_cached(page, page_size)
    if cached_result:
        return cached_result
    
    # Query from database
    offset = (page - 1) * page_size
    
    users = db.query(User).filter(
        User.predictions_count > 0
    ).order_by(
        desc(User.total_points),
        desc(User.correct_results)
    ).offset(offset).limit(page_size).all()
    
    total_users = db.query(User).filter(User.predictions_count > 0).count()
    
    leaderboard = []
    for idx, user in enumerate(users, start=offset + 1):
        leaderboard.append({
            "rank": idx,
            "user_id": user.id,
            "username": user.username,
            "total_points": user.total_points,
            "predictions_count": user.predictions_count,
            "accuracy": user.accuracy,
            "exact_scores": user.exact_scores
        })
    
    result = {
        "leaderboard": leaderboard,
        "total_users": total_users,
        "page": page,
        "page_size": page_size
    }
    
    # Cache result
    leaderboard_service.cache_global_leaderboard(page, page_size, result)
    
    return result


@router.get("/league/{league_id}")
async def get_league_leaderboard(
    league_id: int,
    db: Session = Depends(get_db)
):
    """
    Get leaderboard for a specific league.
    
    - **league_id**: League ID
    """
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    # Get all memberships with user details
    memberships = db.query(LeagueMembership).filter(
        LeagueMembership.league_id == league_id,
        LeagueMembership.is_active == True
    ).order_by(
        desc(LeagueMembership.league_points)
    ).all()
    
    leaderboard = []
    for idx, membership in enumerate(memberships, start=1):
        membership.league_rank = idx  # Update rank
        
        leaderboard.append({
            "rank": idx,
            "user_id": membership.user_id,
            "username": membership.user.username,
            "league_points": membership.league_points,
            "predictions_count": membership.user.predictions_count,
            "accuracy": membership.user.accuracy
        })
    
    db.commit()
    
    return {
        "league_id": league_id,
        "league_name": league.name,
        "leaderboard": leaderboard,
        "total_members": len(leaderboard)
    }


@router.post("/league", response_model=LeagueResponse, status_code=status.HTTP_201_CREATED)
async def create_league(
    league_data: LeagueCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new private league.
    
    - **name**: League name
    - **description**: Optional description
    - **max_members**: Maximum members (default: 50)
    - **is_private**: Private league (default: True)
    
    Requires authentication.
    """
    # Generate unique invite code
    invite_code = League.generate_invite_code()
    
    # Ensure uniqueness
    while db.query(League).filter(League.invite_code == invite_code).first():
        invite_code = League.generate_invite_code()
    
    # Create league
    league = League(
        name=league_data.name,
        description=league_data.description,
        invite_code=invite_code,
        owner_id=current_user.id,
        max_members=league_data.max_members,
        is_private=league_data.is_private
    )
    
    db.add(league)
    db.commit()
    db.refresh(league)
    
    # Add owner as first member
    membership = LeagueMembership(
        user_id=current_user.id,
        league_id=league.id
    )
    db.add(membership)
    db.commit()
    
    return league


@router.post("/league/{league_id}/join")
async def join_league(
    league_id: int,
    invite_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Join a league using invite code.
    
    - **league_id**: League ID
    - **invite_code**: League invite code
    
    Requires authentication.
    """
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    # Verify invite code
    if league.invite_code != invite_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid invite code"
        )
    
    # Check if league is full
    if league.is_full:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="League is full"
        )
    
    # Check if already a member
    existing = db.query(LeagueMembership).filter(
        LeagueMembership.user_id == current_user.id,
        LeagueMembership.league_id == league_id
    ).first()
    
    if existing:
        if existing.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already a member of this league"
            )
        else:
            # Reactivate membership
            existing.is_active = True
            db.commit()
            return {"message": "Rejoined league successfully"}
    
    # Create membership
    membership = LeagueMembership(
        user_id=current_user.id,
        league_id=league_id,
        league_points=current_user.total_points  # Initialize with current points
    )
    
    db.add(membership)
    db.commit()
    
    return {
        "message": "Joined league successfully",
        "league_id": league_id,
        "league_name": league.name
    }


@router.get("/league/code/{invite_code}", response_model=LeagueResponse)
async def get_league_by_code(
    invite_code: str,
    db: Session = Depends(get_db)
):
    """
    Get league details by invite code.
    
    - **invite_code**: League invite code
    """
    league = db.query(League).filter(League.invite_code == invite_code).first()
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    return league


@router.get("/user/leagues")
async def get_user_leagues(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all leagues the current user is a member of.
    
    Requires authentication.
    """
    memberships = db.query(LeagueMembership).filter(
        LeagueMembership.user_id == current_user.id,
        LeagueMembership.is_active == True
    ).all()
    
    leagues = []
    for membership in memberships:
        league = membership.league
        leagues.append({
            "league_id": league.id,
            "name": league.name,
            "member_count": league.member_count,
            "is_owner": league.owner_id == current_user.id,
            "my_rank": membership.league_rank,
            "my_points": membership.league_points
        })
    
    return leagues


@router.post("/league/{league_id}/leave")
async def leave_league(
    league_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Leave a league.
    
    - **league_id**: League ID
    
    Requires authentication.
    """
    membership = db.query(LeagueMembership).filter(
        LeagueMembership.user_id == current_user.id,
        LeagueMembership.league_id == league_id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="Not a member of this league")
    
    league = db.query(League).filter(League.id == league_id).first()
    
    # Prevent owner from leaving (must transfer ownership first)
    if league.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="League owner cannot leave. Delete the league or transfer ownership."
        )
    
    membership.is_active = False
    db.commit()
    
    return {"message": "Left league successfully"}


@router.get("/rank/{user_id}")
async def get_user_rank(user_id: int, db: Session = Depends(get_db)):
    """
    Get global rank for a specific user.
    
    - **user_id**: User ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Count users with more points
    rank = db.query(User).filter(
        User.total_points > user.total_points
    ).count() + 1
    
    total_users = db.query(User).filter(User.predictions_count > 0).count()
    
    return {
        "user_id": user_id,
        "username": user.username,
        "rank": rank,
        "total_points": user.total_points,
        "total_users": total_users,
        "percentile": round((1 - rank / total_users) * 100, 1) if total_users > 0 else 0
    }
