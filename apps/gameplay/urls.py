from django.urls import path
from . import quiz_stats

from .leaderboard_api import LeaderboardStatsAPIView, AddLeaderboardParticipantAPIView, GameSessionAPIView, GetChallengesAPIView, StartChallengeAPIView
from .submit_answer_api import SubmitAnswerAPIView
from .quiz_questions_api import QuizQuestionsAPIView

urlpatterns = [
    path('quiz_questions/', QuizQuestionsAPIView.as_view(), name='quiz_questions_api'),
    path('submit_answer/', SubmitAnswerAPIView.as_view(), name='submit_answer'),
    path('leaderboard_stats/', quiz_stats.leaderboard_stats, name='leaderboard_stats'),
    path('leaderboard_stats_api/', LeaderboardStatsAPIView.as_view(), name='leaderboard_stats_api'),
    path('add_leaderboard_participant/', AddLeaderboardParticipantAPIView.as_view(), name='add_leaderboard_participant'),
    path('game_session/', GameSessionAPIView.as_view(), name='game_session'),
    path('challenges/', GetChallengesAPIView.as_view(), name='get_challenges'),
    path('start_challenge/', StartChallengeAPIView.as_view(), name='start_challenge'),
]
