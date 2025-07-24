import logging
from concurrent.futures import ThreadPoolExecutor
from django.db import connection
from django.db.models import Count, Sum, Avg
from django.core.cache import caches
from rest_framework.response import Response
from rest_framework.decorators import api_view
from caching import utils

from .models import Quiz, QuizSession, Bidang

logger = logging.getLogger(__name__)

leaderboard_cache = caches['leaderboards']
user_stats_cache = caches['user_stats']


@api_view(['GET'])
def optimized_subject_leaderboard_view(request):
    """
    Optimized leaderboard by subject using individual bidang caching
    """
    bidang = request.query_params.get('bidang')
    
    if bidang:
        cache_key = utils.generate_leaderboard_cache_key(bidang)
        
        cached_data = leaderboard_cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Cache hit for subject leaderboard: {cache_key}")
            response = Response(cached_data)
            return response
        
        results = (
            QuizSession.objects
            .filter(quiz__bidang=bidang)
            .values('user__id', 'user__username', 'quiz__bidang')
            .annotate(
                total_score=Sum('score'),
                quiz_count=Count('id'),
                average_score=Avg('score'),
                total_duration=Sum('duration'),
                average_duration=Avg('duration'),
            )
            .order_by('-total_score', 'average_duration')
        )
        
        leaderboard_data = []
        bidang_name = dict(Bidang.choices).get(bidang, bidang)
        
        for rank, row in enumerate(results, 1):
            leaderboard_data.append({
                'rank': rank,
                'user_id': row['user__id'],
                'username': row['user__username'],
                'bidang': row['quiz__bidang'],
                'bidang_name': bidang_name,
                'total_score': row['total_score'],
                'quiz_count': row['quiz_count'],
                'average_score': round(row['average_score'], 2) if row['average_score'] else 0,
                'total_duration': row['total_duration'],
                'average_duration': round(row['average_duration'], 2) if row['average_duration'] else 0
            })
        
        response_data = {
            'bidang': bidang,
            'bidang_name': bidang_name,
            'total_participants': len(leaderboard_data),
            'leaderboard': leaderboard_data
        }
        
        leaderboard_cache.set(cache_key, response_data, 180)
        logger.info(f"Cached subject leaderboard: {cache_key}")
        
        return Response(response_data)
    
    else:
        def get_subject_leaderboard(bidang_choice):
            bidang_code, bidang_name = bidang_choice
            cache_key = utils.generate_leaderboard_cache_key(bidang_code)
            
            cached_subject_data = leaderboard_cache.get(cache_key)
            if cached_subject_data is not None:
                logger.info(f"Cache hit for subject {bidang_code}: {cache_key}")
                return bidang_code, {
                    'bidang_name': bidang_name,
                    'total_participants': cached_subject_data.get('total_participants', 0),
                    'leaderboard': cached_subject_data['leaderboard']
                }

            results = (
                QuizSession.objects
                .filter(quiz__bidang=bidang_code)
                .values('user__id', 'user__username', 'quiz__bidang')
                .annotate(
                    total_score=Sum('score'),
                    quiz_count=Count('id'),
                    average_score=Avg('score'),
                    total_duration=Sum('duration'),
                    average_duration=Avg('duration'),
                )
                .order_by('-total_score', 'average_duration')
            )
            
            formatted_data = []
            for rank, row in enumerate(results, 1):
                formatted_data.append({
                    'rank': rank,
                    'user_id': row['user__id'],
                    'username': row['user__username'],
                    'bidang': row['quiz__bidang'],
                    'bidang_name': bidang_name,
                    'total_score': row['total_score'],
                    'quiz_count': row['quiz_count'],
                    'average_score': round(row['average_score'], 2) if row['average_score'] else 0,
                    'total_duration': row['total_duration'],
                    'average_duration': round(row['average_duration'], 2) if row['average_duration'] else 0
                })
            
            bidang_cache_data = {
                'bidang': bidang_code,
                'bidang_name': bidang_name,
                'total_participants': len(formatted_data),
                'leaderboard': formatted_data
            }
            leaderboard_cache.set(cache_key, bidang_cache_data, 180)
            logger.info(f"Cached subject leaderboard for {bidang_code}: {cache_key}")
            
            return bidang_code, {
                'bidang_name': bidang_name,
                'total_participants': len(formatted_data),
                'leaderboard': formatted_data
            }
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(get_subject_leaderboard, choice) for choice in Bidang.choices]
            results = [future.result() for future in futures]
        
        response_data = {bidang_code: data for bidang_code, data in results}
    
    response = Response(response_data)
    return response


@api_view(['GET'])
def optimized_quiz_leaderboard_view(request, pk):
    """
    Optimized leaderboard by quiz using caching
    """
    
    cache_key = utils.generate_quiz_leaderboard_cache_key(pk)
    
    cached_data = leaderboard_cache.get(cache_key)
    if cached_data is not None:
        logger.info(f"Cache hit for quiz leaderboard: {cache_key}")
        response = Response(cached_data)
        return response
    
    try:
        quiz = Quiz.objects.only('id', 'title').get(id=pk)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz not found'}, status=404)
    
    results = (
        QuizSession.objects
        .filter(quiz_id=pk)
        .select_related('user')
        .order_by('-score', 'duration')
        .all()
    )
    
    leaderboard_data = []
    for rank, row in enumerate(results, 1):
        leaderboard_data.append({
            'rank': rank,
            'session_id': row.id,
            'user_id': row.user.id,
            'username': row.user.username,
            'score': row.score,
            'duration': row.duration,
            'user_start': row.user_start.isoformat() if row.user_start else None,
            'user_end': row.user_end.isoformat() if row.user_end else None,
        })
    
    response_data = {
        'quiz_id': quiz.id,
        'quiz_title': quiz.title,
        'total_participants': len(leaderboard_data),
        'leaderboard': leaderboard_data
    }
    
    leaderboard_cache.set(cache_key, response_data, 180)
    logger.info(f"Cached quiz leaderboard: {cache_key}")
    
    response = Response(response_data)
    return response


@api_view(['GET'])
def optimized_user_quiz_performance_view(request, pk):
    """
    Optimized user performance using caching
    """
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=401)
    
    user_id = request.user.id
    cache_key = utils.generate_quiz_leaderboard_by_user_cache_key(pk, user_id)
    
    cached_data = user_stats_cache.get(cache_key)
    if cached_data is not None:
        logger.info(f"Cache hit for user performance: {cache_key}")
        response = Response(cached_data)
        return response
    
    try:
        quiz = Quiz.objects.only('id', 'title').get(id=pk)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz not found'}, status=404)
    
    try:
        user_session = QuizSession.objects.select_related('user').get(
            quiz_id=pk, user=request.user
        )
    except QuizSession.DoesNotExist:
        return Response({'error': 'No quiz session found'}, status=404)
    
    qs = QuizSession.objects.filter(quiz_id=pk)
    user_rank = (
        qs.filter(
            score__gt=user_session.score
        ).count()
        +
        qs.filter(
            score=user_session.score,
            duration__lt=user_session.duration
        ).count()
        + 1
    )
    total_participants = qs.count()
        
    response_data = {
        'quiz_id': quiz.id,
        'quiz_title': quiz.title,
        'user_performance': {
            'user_id': user_id,
            'username': request.user.username,
            'session': {
                'id': user_session.id,
                'score': user_session.score,
                'duration': user_session.duration,
                'user_start': user_session.user_start.isoformat(),
                'user_end': user_session.user_end.isoformat(),
            },
            'rank': user_rank,
            'total_participants': total_participants,
        }
    }
    
    user_stats_cache.set(cache_key, response_data, 3600)
    logger.info(f"Cached user performance: {cache_key}")
    
    response = Response(response_data)
    return response
