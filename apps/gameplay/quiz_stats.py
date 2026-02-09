from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Question, Challenge

import json

# Model to store quiz statistics
class QuizStat(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, null=True, blank=True)
    question_id = models.IntegerField()
    is_correct = models.BooleanField()
    time_taken = models.FloatField(default=0.0, help_text="Time taken to answer in seconds")
    timestamp = models.DateTimeField(default=timezone.now)





# Real answer-checking function
def check_answer(question_id, answer):
    try:
        question = Question.objects.get(id=question_id)
        return str(answer).strip().lower() == str(question.correct_answer).strip().lower()
    except Question.DoesNotExist:
        return False

# Endpoint to submit answer and determine correctness
@csrf_exempt
@require_POST
def submit_answer(request):
    data = json.loads(request.body)
    unique_code = data['user_id']
    question_id = data['question_id']
    answer = data['answer']
    user = get_user_model().objects.get(unique_code=unique_code)
    is_correct = check_answer(question_id, answer)
    QuizStat.objects.create(user=user, question_id=question_id, is_correct=is_correct)
    return JsonResponse({'status': 'ok', 'is_correct': is_correct})

# Endpoint to aggregate statistics for leaderboard
@csrf_exempt
@require_POST
def leaderboard_stats(request):
    data = json.loads(request.body)
    user_ids = data.get('user_ids', [])
    stats = []
    for user in get_user_model().objects.filter(id__in=user_ids):
        user_stats = QuizStat.objects.filter(user=user)
        total_answered = user_stats.count()
        total_correct = user_stats.filter(is_correct=True).count()
        total_failed = user_stats.filter(is_correct=False).count()
        last_question = user_stats.order_by('-timestamp').first()
        stats.append({
            'user_id': user.id,
            'username': user.username,
            'current_question': last_question.question_id if last_question else None,
            'total_answered': total_answered,
            'total_correct': total_correct,
            'total_failed': total_failed,
        })
    return JsonResponse({'leaderboard': stats})

