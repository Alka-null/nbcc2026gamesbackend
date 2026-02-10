from django.contrib import admin

from .models import QuizResult, GameAnswer, GameSession, Challenge


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'score', 'total_questions', 'created_at')
    search_fields = ('display_name', 'player__name', 'player__email')
    list_filter = ('created_at',)
    ordering = ('-score', '-created_at')


@admin.register(GameAnswer)
class GameAnswerAdmin(admin.ModelAdmin):
    list_display = ('player', 'game_type', 'question_id', 'is_correct', 'time_taken_seconds', 'created_at')
    search_fields = ('player__name', 'player__email', 'question_text')
    list_filter = ('game_type', 'is_correct', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('player', 'game_type', 'correct_answers', 'total_questions', 'score_percentage', 'completed', 'started_at')
    search_fields = ('player__name', 'player__email')
    list_filter = ('game_type', 'completed', 'started_at')
    ordering = ('-started_at',)
    readonly_fields = ('started_at', 'score_percentage')


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'started_at', 'ended_at')
    list_filter = ('is_active',)
    ordering = ('-started_at',)
