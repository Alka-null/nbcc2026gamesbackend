from django.contrib import admin

from .models import QuizResult


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'score', 'total_questions', 'created_at')
    search_fields = ('display_name', 'player__name', 'player__email')
    list_filter = ('created_at',)
    ordering = ('-score', '-created_at')
