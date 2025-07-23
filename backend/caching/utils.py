from django.core.cache import cache
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def generate_leaderboard_cache_key(bidang: Optional[str] = None) -> str:
    """
    Generate cache key for subject leaderboard.
    
    Args:
        bidang: Subject code (optional, defaults to 'all')
        
    Returns:
        Cache key string
    """
    return f"leaderboard:subject:{bidang or 'all'}"

def generate_quiz_leaderboard_cache_key(quiz_id: int) -> str:
    """
    Generate cache key for quiz-specific leaderboard.
    
    Args:
        quiz_id: Quiz ID
        
    Returns:
        Cache key string
    """
    return f"leaderboard:quiz:{quiz_id}"

def generate_quiz_leaderboard_by_user_cache_key(quiz_id: int, user_id: int) -> str:
    """
    Generate cache key for quiz and user specific leaderboard.
    
    Args:
        quiz_id: Quiz ID
        user_id: User ID
        
    Returns:
        Cache key string
    """
    return f"user_performance:quiz:{quiz_id}:user:{user_id}"

def invalidate_leaderboard_caches(bidang: Optional[str] = None):
    """
    Invalidate leaderboard caches for a specific subject or all subjects.
    
    Args:
        bidang: Subject code to invalidate (optional, invalidates all if None)
    """
    try:
        if bidang:
            cache_key = generate_leaderboard_cache_key(bidang)
            cache.delete(cache_key)
            logger.info(f"Invalidated leaderboard cache for subject: {bidang}")
        else:
            # Invalidate individual subject caches only (no "all subjects" cache)
            from api.models import Bidang
            
            for bidang_choice in Bidang.choices:
                subject_key = generate_leaderboard_cache_key(bidang_choice[0])
                cache.delete(subject_key)
            
            logger.info("Invalidated all individual subject leaderboard caches")
            
    except Exception as e:
        logger.error(f"Failed to invalidate leaderboard caches: {e}")


def invalidate_quiz_leaderboard_cache(quiz_id: int):
    """
    Invalidate leaderboard cache for a specific quiz.
    
    Args:
        quiz_id: Quiz ID to invalidate cache for
    """
    try:
        cache_key = generate_quiz_leaderboard_cache_key(quiz_id)
        cache.delete(cache_key)
        logger.info(f"Invalidated leaderboard cache for quiz: {quiz_id}")
        
    except Exception as e:
        logger.error(f"Failed to invalidate quiz leaderboard cache: {e}")


def invalidate_quiz_leaderboard_by_user_cache(quiz_id: int, user_id: int):
    """
    Invalidate leaderboard cache for a specific quiz and user.
    
    Args:
        quiz_id: Quiz ID to invalidate user performance caches for
        user_id: User ID to invalidate cache for
    """
    try:
        cache_key = generate_quiz_leaderboard_by_user_cache_key(quiz_id, user_id)
        cache.delete(cache_key)
        logger.info(f"Invalidated user: {user_id}'s performance cache for quiz: {quiz_id}")

    except Exception as e:
        logger.error(f"Failed to invalidate user performance cache: {e}")
