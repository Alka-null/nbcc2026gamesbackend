from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from apps.accounts.models import Player
from .models import GameAnswer, GameSession, GameType


class SubmitGameAnswerAPIView(APIView):
    """
    Submit a single game answer.

    POST /api/gameplay/game-answer/
    """

    def post(self, request):
        data = request.data
        player_code = data.get('player_code', '').strip().upper()
        game_type = data.get('game_type', '')
        question_id = data.get('question_id', 0)
        question_text = data.get('question_text', '')
        selected_answer = data.get('selected_answer', '')
        correct_answer = data.get('correct_answer', '')
        is_correct = data.get('is_correct', False)
        time_taken = data.get('time_taken_seconds', 0.0)

        if not player_code:
            return Response({'error': 'player_code is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            player = Player.objects.get(unique_code=player_code, is_active=True)
        except Player.DoesNotExist:
            return Response({'error': 'Invalid player code'}, status=status.HTTP_404_NOT_FOUND)

        answer = GameAnswer.objects.create(
            player=player,
            game_type=game_type,
            question_id=question_id,
            question_text=question_text,
            selected_answer=selected_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            time_taken_seconds=time_taken,
        )

        return Response({
            'message': 'Answer saved',
            'answer_id': answer.id,
        }, status=status.HTTP_201_CREATED)


class SubmitBulkGameAnswersAPIView(APIView):
    """
    Submit multiple game answers in bulk.

    POST /api/gameplay/game-answers/bulk/

    Expected payload:
    {
        "player_code": "ABC123",
        "game_type": "jigsaw" | "drag_drop",
        "answers": [
            {
                "question_id": 1,
                "question_text": "...",
                "selected_answer": "...",
                "correct_answer": "...",
                "is_correct": true/false,
                "time_taken_seconds": 0.0
            },
            ...
        ]
    }
    """

    def post(self, request):
        data = request.data
        player_code = data.get('player_code', '').strip().upper()
        game_type = data.get('game_type', '')
        answers = data.get('answers', [])

        if not player_code:
            return Response({'error': 'player_code is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not game_type:
            return Response({'error': 'game_type is required'}, status=status.HTTP_400_BAD_REQUEST)

        valid_types = [choice[0] for choice in GameType.choices]
        if game_type not in valid_types:
            return Response(
                {'error': f'Invalid game_type. Must be one of: {valid_types}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not answers or not isinstance(answers, list):
            return Response({'error': 'answers list is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            player = Player.objects.get(unique_code=player_code, is_active=True)
        except Player.DoesNotExist:
            return Response({'error': 'Invalid player code'}, status=status.HTTP_404_NOT_FOUND)

        created = []
        for i, ans in enumerate(answers):
            obj = GameAnswer.objects.create(
                player=player,
                game_type=game_type,
                question_id=ans.get('question_id', i + 1),
                question_text=ans.get('question_text', ''),
                selected_answer=ans.get('selected_answer', ''),
                correct_answer=ans.get('correct_answer', ''),
                is_correct=ans.get('is_correct', False),
                time_taken_seconds=ans.get('time_taken_seconds', 0.0),
            )
            created.append(obj.id)

        # Also create/update a GameSession summary
        correct_count = sum(1 for a in answers if a.get('is_correct', False))
        total_time = sum(float(a.get('time_taken_seconds', 0)) for a in answers)

        GameSession.objects.create(
            player=player,
            game_type=game_type,
            total_questions=len(answers),
            correct_answers=correct_count,
            total_time_seconds=total_time,
            completed=True,
            completed_at=timezone.now(),
        )

        return Response({
            'message': f'{len(created)} answers saved',
            'answer_ids': created,
        }, status=status.HTTP_201_CREATED)


class SaveGameSessionAPIView(APIView):
    """
    Save a game session summary.

    POST /api/gameplay/game-session/save/
    """

    def post(self, request):
        data = request.data
        player_code = data.get('player_code', '').strip().upper()
        game_type = data.get('game_type', '')
        total_questions = data.get('total_questions', 0)
        correct_answers = data.get('correct_answers', 0)
        total_time = data.get('total_time_seconds', 0.0)
        completed = data.get('completed', False)

        if not player_code:
            return Response({'error': 'player_code is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            player = Player.objects.get(unique_code=player_code, is_active=True)
        except Player.DoesNotExist:
            return Response({'error': 'Invalid player code'}, status=status.HTTP_404_NOT_FOUND)

        session = GameSession.objects.create(
            player=player,
            game_type=game_type,
            total_questions=total_questions,
            correct_answers=correct_answers,
            total_time_seconds=total_time,
            completed=completed,
            completed_at=timezone.now() if completed else None,
        )

        return Response({
            'message': 'Session saved',
            'session_id': session.id,
        }, status=status.HTTP_201_CREATED)


class GetPlayerGameStatsAPIView(APIView):
    """
    Get game statistics for a player.

    GET /api/gameplay/player-stats/?player_code=ABC123
    """

    def get(self, request):
        player_code = request.query_params.get('player_code', '').strip().upper()

        if not player_code:
            return Response({'error': 'player_code is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            player = Player.objects.get(unique_code=player_code, is_active=True)
        except Player.DoesNotExist:
            return Response({'error': 'Invalid player code'}, status=status.HTTP_404_NOT_FOUND)

        sessions = GameSession.objects.filter(player=player)
        stats = {}
        for game_type, label in GameType.choices:
            game_sessions = sessions.filter(game_type=game_type)
            if game_sessions.exists():
                best = game_sessions.order_by('-correct_answers').first()
                stats[game_type] = {
                    'label': label,
                    'total_sessions': game_sessions.count(),
                    'best_score': best.correct_answers,
                    'best_total': best.total_questions,
                    'best_time': best.total_time_seconds,
                }

        return Response({
            'player_code': player_code,
            'player_name': player.name,
            'stats': stats,
        })
