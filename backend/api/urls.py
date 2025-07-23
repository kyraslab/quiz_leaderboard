from django.urls import path
from .views import (
    QuizListView, QuizDetailView,
    QuizSessionListCreateView, QuizSessionDetailView,
    subject_leaderboard_view, quiz_leaderboard_view, user_quiz_performance_view
)
from .optimized_views import (
    optimized_subject_leaderboard_view, optimized_quiz_leaderboard_view,
    optimized_user_quiz_performance_view
)

urlpatterns = [
    # Original views (basic, no caching)
    path('quizzes/', QuizListView.as_view(), name='quiz-list'),
    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quiz-sessions/', QuizSessionListCreateView.as_view(), name='quiz-session-list-create'),
    path('quiz-sessions/<int:pk>/', QuizSessionDetailView.as_view(), name='quiz-session-detail'),
    path('leaderboard/subject/', subject_leaderboard_view, name='subject-leaderboard'),
    path('leaderboard/quiz/<int:pk>/', quiz_leaderboard_view, name='quiz-leaderboard'),
    path('leaderboard/quiz/<int:pk>/user-performance/', user_quiz_performance_view, name='user-quiz-performance'),
    
    # Optimized leaderboard views (high performance with caching)
    path('optimized/leaderboard/subject/', optimized_subject_leaderboard_view, name='optimized-subject-leaderboard'),
    path('optimized/leaderboard/quiz/<int:pk>/', optimized_quiz_leaderboard_view, name='optimized-quiz-leaderboard'),
    path('optimized/leaderboard/quiz/<int:pk>/user-performance/', optimized_user_quiz_performance_view, name='optimized-user-quiz-performance'),
]