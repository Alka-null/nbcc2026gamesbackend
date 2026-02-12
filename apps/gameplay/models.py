
from django.db import models
from django.conf import settings

# Game types for answer tracking
class GameType(models.TextChoices):
    DRAG_DROP = 'drag_drop', 'Drag & Drop Game'
    BEER_CUP = 'beer_cup', 'Beer Cup Game'
    JIGSAW = 'jigsaw', 'Jigsaw Puzzle Game'

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


class GameAnswer(models.Model):
    """Model to track individual answers from game challenges"""
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='game_answers',
    )
    game_type = models.CharField(
        max_length=20,
        choices=GameType.choices,
    )
    question_id = models.IntegerField(help_text="Question ID from the game")
    question_text = models.TextField(blank=True, help_text="The question text for reference")
    selected_answer = models.TextField(help_text="The answer selected by the player")
    correct_answer = models.TextField(blank=True, help_text="The correct answer for reference")
    is_correct = models.BooleanField()
    time_taken_seconds = models.FloatField(default=0.0, help_text="Time taken to answer in seconds")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['player', 'game_type']),
            models.Index(fields=['game_type', 'created_at']),
        ]

    def __str__(self):
        status = "✓" if self.is_correct else "✗"
        return f"{self.player} - {self.game_type} Q{self.question_id} {status}"


class GameSession(models.Model):
    """Model to track a complete game session"""
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='game_sessions',
    )
    game_type = models.CharField(
        max_length=20,
        choices=GameType.choices,
    )
    total_questions = models.PositiveSmallIntegerField()
    correct_answers = models.PositiveSmallIntegerField()
    total_time_seconds = models.FloatField(default=0.0)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.player} - {self.game_type} ({self.correct_answers}/{self.total_questions})"

    @property
    def score_percentage(self):
        if self.total_questions == 0:
            return 0
        return round((self.correct_answers / self.total_questions) * 100, 2)


class UserFeedback(models.Model):
    """Model to store user feedback from the event"""
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedbacks',
    )
    unique_code = models.CharField(max_length=50, help_text="Player's unique code")
    full_name = models.CharField(max_length=200, blank=True, default='', help_text="Player's full name")
    cluster_sales_area = models.CharField(max_length=200, blank=True, default='', help_text="Player's cluster or sales area")
    digital_sales_tool = models.CharField(max_length=100, blank=True, null=True, default='', help_text="Selected digital sales tool")
    what_works = models.TextField(blank=True, help_text="What worked well for the user")
    what_is_confusing = models.TextField(blank=True, help_text="What was confusing or unclear")
    what_can_be_better = models.TextField(blank=True, help_text="Suggestions for improvement")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Feedback'
        verbose_name_plural = 'User Feedbacks'
    
    def __str__(self):
        return f"Feedback from {self.unique_code} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
