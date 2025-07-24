from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from .models import Quiz, QuizSession, Bidang
from .serializers import (
    QuizSerializer, QuizSessionSerializer, QuizSessionCreateSerializer,
    SubjectLeaderboardSerializer, QuizLeaderboardSerializer
)
from caching.utils import (
    invalidate_leaderboard_caches, 
    invalidate_quiz_leaderboard_cache,
    invalidate_quiz_leaderboard_by_user_cache,
)
from websocket.utils import websocket_notifier

class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class for list views.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class QuizListView(generics.ListAPIView):
    """
    Get list of all quizzes with pagination
    """
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = Quiz.objects.all()
        bidang = self.request.query_params.get('bidang')
        active_only = self.request.query_params.get('active_only')
        
        if bidang:
            queryset = queryset.filter(bidang=bidang)
        
        if active_only and active_only.lower() == 'true':
            now = timezone.now()
            queryset = queryset.filter(start_date__lte=now, end_date__gte=now)
        
        return queryset.order_by('-start_date')

class QuizDetailView(generics.RetrieveAPIView):
    """
    Get a specific quiz by ID with attempt status for authenticated users
    """
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = serializer.data

        if not request.user.is_authenticated:
            return Response(response_data)
        
        existing_session = QuizSession.objects.filter(quiz=instance, user=request.user).first()
        
        now = timezone.now()
        is_active = instance.start_date <= now <= instance.end_date
        
        response_data['can_attempt'] = is_active and existing_session is None
        response_data['already_attempted'] = existing_session is not None
        response_data['attempt_details'] = None
        
        if existing_session:
            response_data['attempt_details'] = {
                'score': existing_session.score,
                'duration': existing_session.duration,
                'user_start': existing_session.user_start,
                'user_end': existing_session.user_end
            }
        
        if not is_active:
            if now < instance.start_date:
                response_data['status_message'] = 'Quiz has not started yet'
            else:
                response_data['status_message'] = 'Quiz has ended'
        elif existing_session:
            response_data['status_message'] = 'You have already attempted this quiz'
        else:
            response_data['status_message'] = 'You can attempt this quiz'
        
        return Response(response_data)

class QuizSessionListCreateView(generics.ListCreateAPIView):
    """
    Get list of all quiz sessions or create a new one with pagination
    """
    queryset = QuizSession.objects.all()
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuizSessionCreateSerializer
        return QuizSessionSerializer
    
    def get_queryset(self):
        queryset = QuizSession.objects.select_related('user', 'quiz').all()

        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        quiz_id = self.request.query_params.get('quiz_id')
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)
        
        bidang = self.request.query_params.get('bidang')
        if bidang:
            queryset = queryset.filter(quiz__bidang=bidang)
        
        return queryset.order_by('-user_end')
    
    def perform_create(self, serializer):
        """
        Override to invalidate relevant caches and send WebSocket notifications 
        when a new quiz session is created
        """
        instance = serializer.save()
        
        invalidate_leaderboard_caches(instance.quiz.bidang)
        invalidate_quiz_leaderboard_cache(instance.quiz.id)
        invalidate_quiz_leaderboard_by_user_cache(instance.quiz.id, instance.user.id)
        
        quiz_session_data = {
            'session_id': instance.id,
            'user_id': instance.user.id,
            'quiz_id': instance.quiz.id,
            'score': instance.score,
            'timestamp': timezone.now().isoformat()
        }
        websocket_notifier.send_quiz_session_uploaded(quiz_session_data)

        timestamp = timezone.now().isoformat()
        
        leaderboard_data = {
            'update_type': 'quiz_session_added',
            'bidang': instance.quiz.bidang,
            'quiz_id': instance.quiz.id,
            'timestamp': timestamp
        }
        websocket_notifier.send_leaderboard_updated(leaderboard_data)
        websocket_notifier.send_quiz_leaderboard_updated(instance.quiz.id, timestamp)

class QuizSessionDetailView(generics.RetrieveAPIView):
    """
    Get a specific quiz session (read-only)
    """
    queryset = QuizSession.objects.select_related('user', 'quiz').all()
    serializer_class = QuizSessionSerializer

@api_view(['GET'])
def subject_leaderboard_view(request):
    """
    Get subject-based leaderboard - aggregated performance per user per subject
    Shows total/average scores across all quizzes taken by each user in each subject
    """
    bidang = request.query_params.get('bidang')
    
    base_queryset = QuizSession.objects.select_related('user', 'quiz')
    
    if bidang:
        base_queryset = base_queryset.filter(quiz__bidang=bidang)
        
        aggregated_data = base_queryset.values(
            'user_id', 'user__username', 'quiz__bidang'
        ).annotate(
            total_score=Sum('score'),
            quiz_count=Count('id'),
            average_score=Avg('score'),
            total_duration=Sum('duration'),
            average_duration=Avg('duration')
        ).order_by('-total_score', 'average_duration')[:20]
        
        leaderboard_data = []
        for item in aggregated_data:
            leaderboard_data.append({
                'user_id': item['user_id'],
                'username': item['user__username'],
                'bidang': item['quiz__bidang'],
                'bidang_name': dict(Bidang.choices)[item['quiz__bidang']],
                'total_score': item['total_score'],
                'quiz_count': item['quiz_count'],
                'average_score': round(item['average_score'], 2) if item['average_score'] else 0,
                'total_duration': item['total_duration'],
                'average_duration': round(item['average_duration'], 2) if item['average_duration'] else 0
            })
        
        serializer = SubjectLeaderboardSerializer(leaderboard_data, many=True)
        
        response_data = {
            'bidang': bidang,
            'bidang_name': dict(Bidang.choices)[bidang],
            'leaderboard': serializer.data
        }
        
        return Response(response_data)
    
    else:
        leaderboard_data = {}
        
        for bidang_choice in Bidang.choices:
            bidang_code = bidang_choice[0]
            bidang_name = bidang_choice[1]
            
            subject_data = base_queryset.filter(quiz__bidang=bidang_code).values(
                'user_id', 'user__username', 'quiz__bidang'
            ).annotate(
                total_score=Sum('score'),
                quiz_count=Count('id'),
                average_score=Avg('score'),
                total_duration=Sum('duration'),
                average_duration=Avg('duration')
            ).order_by('-total_score', 'average_duration')[:20]
            
            formatted_data = []
            for item in subject_data:
                formatted_data.append({
                    'user_id': item['user_id'],
                    'username': item['user__username'],
                    'bidang': item['quiz__bidang'],
                    'bidang_name': bidang_name,
                    'total_score': item['total_score'],
                    'quiz_count': item['quiz_count'],
                    'average_score': round(item['average_score'], 2) if item['average_score'] else 0,
                    'total_duration': item['total_duration'],
                    'average_duration': round(item['average_duration'], 2) if item['average_duration'] else 0
                })
            
            serializer = SubjectLeaderboardSerializer(formatted_data, many=True)
            
            leaderboard_data[bidang_code] = {
                'bidang_name': bidang_name,
                'leaderboard': serializer.data
            }
        
        return Response(leaderboard_data)


@api_view(['GET'])
def quiz_leaderboard_view(request, pk):
    """
    Get quiz session leaderboard for a specific quiz
    Shows top performances for a specific quiz by quiz ID
    """
    try:
        quiz = Quiz.objects.get(id=pk)
    except Quiz.DoesNotExist:
        return Response(
            {'error': 'Quiz not found'}, 
            status=404
        )
    
    queryset = QuizSession.objects.select_related('user', 'quiz').filter(quiz_id=pk)
    leaderboard = queryset.order_by('-score', 'duration')[:20]
    serializer = QuizLeaderboardSerializer(leaderboard, many=True)
    
    response_data = {
        'quiz_id': quiz.id,
        'quiz_title': quiz.title,
        'leaderboard': serializer.data
    }
    
    return Response(response_data)


@api_view(['GET'])
def user_quiz_performance_view(request, pk):
    """
    Get current logged in user's performance and rank for a specific quiz
    Shows user's scores, rank, and comparison with leaderboard
    """
    try:
        quiz = Quiz.objects.get(id=pk)
    except Quiz.DoesNotExist:
        return Response(
            {'error': 'Quiz not found'}, 
            status=404
        )
    
    user = request.user
    if not user.is_authenticated:
        return Response(
            {'error': 'Authentication required'}, 
            status=401
        )
    
    try:
        user_session = QuizSession.objects.get(quiz_id=pk, user=user)
    except QuizSession.DoesNotExist:
        return Response(
            {'error': 'No quiz session found for this user and quiz'}, 
            status=404
        )
    
    all_sessions = QuizSession.objects.filter(quiz_id=pk).order_by('-score', 'duration')
    
    user_rank = 1
    for session in all_sessions:
        if session.user_id == user.id:
            break
        if (session.score > user_session.score or 
            (session.score == user_session.score and session.duration < user_session.duration)):
            user_rank += 1
    
    total_participants = QuizSession.objects.filter(quiz_id=pk).count()
    
    user_session_serializer = QuizLeaderboardSerializer(user_session)
    
    response_data = {
        'quiz_id': quiz.id,
        'quiz_title': quiz.title,
        'user_performance': {
            'user_id': user.id,
            'username': user.username,
            'session': user_session_serializer.data,
            'rank': user_rank,
            'total_participants': total_participants,
            'percentile': round((1 - (user_rank - 1) / total_participants) * 100, 2) if total_participants > 0 else 0
        }
    }
    
    return Response(response_data)
