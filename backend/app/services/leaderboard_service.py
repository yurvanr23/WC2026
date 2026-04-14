"""
Leaderboard Service

Redis-based caching for leaderboards.
"""

import json
import redis
from typing import Optional, Dict
from app.core.config import settings


class LeaderboardService:
    """Service for leaderboard operations with Redis caching"""
    
    def __init__(self):
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            self.redis_available = True
        except:
            self.redis_client = None
            self.redis_available = False
    
    def get_global_leaderboard_cached(
        self,
        page: int,
        page_size: int
    ) -> Optional[Dict]:
        """
        Get cached global leaderboard.
        
        Args:
            page: Page number
            page_size: Items per page
            
        Returns:
            Cached leaderboard or None
        """
        if not self.redis_available:
            return None
        
        cache_key = f"leaderboard:global:{page}:{page_size}"
        
        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except:
            pass
        
        return None
    
    def cache_global_leaderboard(
        self,
        page: int,
        page_size: int,
        data: Dict
    ):
        """
        Cache global leaderboard.
        
        Args:
            page: Page number
            page_size: Items per page
            data: Leaderboard data to cache
        """
        if not self.redis_available:
            return
        
        cache_key = f"leaderboard:global:{page}:{page_size}"
        
        try:
            self.redis_client.setex(
                cache_key,
                settings.REDIS_CACHE_TTL,
                json.dumps(data)
            )
        except:
            pass
    
    def invalidate_leaderboard_cache(self):
        """Invalidate all leaderboard caches"""
        if not self.redis_available:
            return
        
        try:
            # Delete all leaderboard keys
            keys = self.redis_client.keys("leaderboard:*")
            if keys:
                self.redis_client.delete(*keys)
        except:
            pass
    
    def update_user_rank_realtime(
        self,
        user_id: int,
        points: int
    ):
        """
        Update user rank in real-time sorted set.
        
        Args:
            user_id: User ID
            points: User points
        """
        if not self.redis_available:
            return
        
        try:
            # Add to sorted set (sorted by points)
            self.redis_client.zadd(
                "leaderboard:realtime",
                {str(user_id): points}
            )
        except:
            pass
    
    def get_user_rank_realtime(self, user_id: int) -> Optional[int]:
        """
        Get user rank from real-time sorted set.
        
        Args:
            user_id: User ID
            
        Returns:
            User rank or None
        """
        if not self.redis_available:
            return None
        
        try:
            # Get rank (0-indexed, so add 1)
            rank = self.redis_client.zrevrank("leaderboard:realtime", str(user_id))
            return rank + 1 if rank is not None else None
        except:
            return None
    
    def get_top_users_realtime(self, limit: int = 10) -> list:
        """
        Get top users from real-time sorted set.
        
        Args:
            limit: Number of users to return
            
        Returns:
            List of (user_id, points) tuples
        """
        if not self.redis_available:
            return []
        
        try:
            # Get top users with scores
            results = self.redis_client.zrevrange(
                "leaderboard:realtime",
                0,
                limit - 1,
                withscores=True
            )
            return [(int(user_id), int(score)) for user_id, score in results]
        except:
            return []
