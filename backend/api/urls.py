from django.urls import path
from .views import (
    QuizListView, QuizDetailView,
    QuizSessionListCreateView, QuizSessionDetailView,
    subject_leaderboard_view, quiz_leaderboard_view, user_quiz_performance_view
)

urlpatterns = [
    path('quizzes/', QuizListView.as_view(), name='quiz-list'),
    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quiz-sessions/', QuizSessionListCreateView.as_view(), name='quiz-session-list-create'),
    path('quiz-sessions/<int:pk>/', QuizSessionDetailView.as_view(), name='quiz-session-detail'),
    path('leaderboard/subject/', subject_leaderboard_view, name='subject-leaderboard'),
    path('leaderboard/quiz/<int:pk>/', quiz_leaderboard_view, name='quiz-leaderboard'),
    path('leaderboard/quiz/<int:pk>/user-performance/', user_quiz_performance_view, name='user-quiz-performance'),
]