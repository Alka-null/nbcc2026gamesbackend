
from django.db import models
from django.conf import settings

# Challenge model for managing quiz challenges
class Challenge(models.Model):
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"

class Question(models.Model):
    text = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)


class QuizResult(models.Model):
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quiz_results',
    )
    display_name = models.CharField(max_length=120, blank=True)
    score = models.PositiveSmallIntegerField()
    total_questions = models.PositiveSmallIntegerField()
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', '-created_at']

    def __str__(self) -> str:
        return f"{self.player_name} - {self.score}/{self.total_questions}"

    @property
    def player_name(self) -> str:
        if self.player_id and self.player:
            return self.player.name
        return self.display_name or 'Guest'
