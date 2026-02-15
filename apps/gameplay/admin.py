from django.contrib import admin

from .models import QuizResult, GameAnswer, GameSession, Challenge, UserFeedback


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
    list_display = ('player', 'game_type', 'correct_answers', 'total_questions', 'score_percentage',
                    'is_correct', 'set_a_score', 'set_a_total', 'set_b_score', 'set_b_total',
                    'completed', 'started_at')
    search_fields = ('player__name', 'player__email')
    list_filter = ('game_type', 'completed', 'is_correct', 'started_at')
    ordering = ('-started_at',)
    readonly_fields = ('started_at', 'score_percentage', 'formatted_answers_data')

    fieldsets = (
        ('Player & Game', {
            'fields': ('player', 'game_type', 'completed', 'is_correct')
        }),
        ('Scores', {
            'fields': ('total_questions', 'correct_answers', 'total_time_seconds', 'score_percentage')
        }),
        ('Set Scores (Drag & Drop)', {
            'fields': ('set_a_score', 'set_a_total', 'set_b_score', 'set_b_total'),
            'classes': ('collapse',),
        }),
        ('Answers Data', {
            'fields': ('formatted_answers_data',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at'),
            'classes': ('collapse',),
        }),
    )

    def formatted_answers_data(self, obj):
        import json
        if obj.answers_data:
            return json.dumps(obj.answers_data, indent=2)
        return '-'
    formatted_answers_data.short_description = 'Answers Data (JSON)'


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'started_at', 'ended_at')
    list_filter = ('is_active',)
    ordering = ('-started_at',)


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'cluster_sales_area', 'unique_code', 'short_what_works', 'short_what_confusing', 'short_what_better', 'created_at')
    search_fields = ('unique_code', 'full_name', 'cluster_sales_area', 'player__name', 'what_works', 'what_is_confusing', 'what_can_be_better')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Player Info', {
            'fields': ('full_name', 'cluster_sales_area', 'digital_sales_tool', 'unique_code', 'player')
        }),
        ('Feedback', {
            'fields': ('what_works', 'what_is_confusing', 'what_can_be_better')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def short_what_works(self, obj):
        return obj.what_works[:50] + '...' if len(obj.what_works) > 50 else obj.what_works
    short_what_works.short_description = 'What Works'
    
    def short_what_confusing(self, obj):
        return obj.what_is_confusing[:50] + '...' if len(obj.what_is_confusing) > 50 else obj.what_is_confusing
    short_what_confusing.short_description = 'What\'s Confusing'
    
    def short_what_better(self, obj):
        return obj.what_can_be_better[:50] + '...' if len(obj.what_can_be_better) > 50 else obj.what_can_be_better
    short_what_better.short_description = 'What Can Be Better'
