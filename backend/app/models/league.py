"""
League Models

Private leagues for competitive predictions among friends.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import secrets

from app.core.database import Base


class League(Base):
    """Private league for group competitions"""
    
    __tablename__ = "leagues"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # League details
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    invite_code = Column(String(20), unique=True, nullable=False, index=True)
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Settings
    is_private = Column(Boolean, default=True, nullable=False)
    max_members = Column(Integer, default=50)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="owned_leagues")
    memberships = relationship("LeagueMembership", back_populates="league", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<League(id={self.id}, name='{self.name}', members={len(self.memberships)})>"
    
    @staticmethod
    def generate_invite_code() -> str:
        """Generate unique invite code"""
        return secrets.token_urlsafe(12)
    
    @property
    def member_count(self) -> int:
        """Get number of members"""
        return len(self.memberships)
    
    @property
    def is_full(self) -> bool:
        """Check if league is at capacity"""
        return self.member_count >= self.max_members


class LeagueMembership(Base):
    """Membership in a league"""
    
    __tablename__ = "league_memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Membership details
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # League-specific stats
    league_points = Column(Integer, default=0, nullable=False)
    league_rank = Column(Integer)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'league_id', name='unique_user_league'),
    )
    
    # Relationships
    user = relationship("User", back_populates="league_memberships")
    league = relationship("League", back_populates="memberships")
    
    def __repr__(self):
        return f"<LeagueMembership(user={self.user_id}, league={self.league_id}, points={self.league_points})>"
