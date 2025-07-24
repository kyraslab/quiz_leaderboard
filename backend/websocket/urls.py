from django.urls import re_path
from . import consumers

urlpatterns = [
    re_path(r'^ws/leaderboard/$', consumers.LeaderboardConsumer.as_asgi()),
]
