"""
API endpoints for saving game answers from Drag & Drop and Beer Cup games.
"""
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import GameAnswer, GameSession, GameType


# Serializers
class GameAnswerSerializer(serializers.Serializer):
    """Serializer for submitting a single game answer"""
    user_code = serializers.CharField(max_length=12, help_text="User's unique_code")
    game_type = serializers.ChoiceField(choices=GameType.choices, help_text="Type of game (drag_drop or beer_cup)")
    question_id = serializers.IntegerField(help_text="Question ID from the game")
    question_text = serializers.CharField(required=False, allow_blank=True, help_text="The question text")
    selected_answer = serializers.CharField(help_text="The answer selected by the player")
    correct_answer = serializers.CharField(required=False, allow_blank=True, help_text="The correct answer")
    is_correct = serializers.BooleanField(help_text="Whether the answer is correct")
    time_taken_seconds = serializers.FloatField(required=False, default=0.0, help_text="Time taken to answer")


class GameAnswerResponseSerializer(serializers.Serializer):
    """Response serializer for game answer submission"""
    status = serializers.CharField()
    message = serializers.CharField()
    answer_id = serializers.IntegerField(required=False)


class BulkGameAnswerSerializer(serializers.Serializer):
    """Serializer for submitting multiple game answers at once"""
    user_code = serializers.CharField(max_length=12, help_text="User's unique_code")
    game_type = serializers.ChoiceField(choices=GameType.choices, help_text="Type of game")
    answers = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of answers with question_id, selected_answer, correct_answer, is_correct, question_text, time_taken_seconds"
    )
    total_time_seconds = serializers.FloatField(required=False, default=0.0, help_text="Total time for the game session")


class GameSessionSerializer(serializers.Serializer):
    """Serializer for game session data"""
    user_code = serializers.CharField(max_length=12, help_text="User's unique_code")
    game_type = serializers.ChoiceField(choices=GameType.choices, help_text="Type of game")
    total_questions = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    total_time_seconds = serializers.FloatField(required=False, default=0.0)


class GameSessionResponseSerializer(serializers.Serializer):
    """Response serializer for game session"""
    status = serializers.CharField()
    message = serializers.CharField()
    session_id = serializers.IntegerField(required=False)
    score_percentage = serializers.FloatField(required=False)


# API Views
class SubmitGameAnswerAPIView(APIView):
    """Submit a single answer from a game"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Submit a single game answer. user_code should be the player's unique_code.",
        request_body=GameAnswerSerializer,
        responses={
            200: GameAnswerResponseSerializer,
            404: "User not found",
            400: "Invalid data"
        }
    )
    def post(self, request):
        serializer = GameAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_code = serializer.validated_data['user_code']
        
        User = get_user_model()
        try:
            user = User.objects.get(unique_code=user_code)
        except User.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        answer = GameAnswer.objects.create(
            player=user,
            game_type=serializer.validated_data['game_type'],
            question_id=serializer.validated_data['question_id'],
            question_text=serializer.validated_data.get('question_text', ''),
            selected_answer=serializer.validated_data['selected_answer'],
            correct_answer=serializer.validated_data.get('correct_answer', ''),
            is_correct=serializer.validated_data['is_correct'],
            time_taken_seconds=serializer.validated_data.get('time_taken_seconds', 0.0),
        )
        
        return Response({
            'status': 'success',
            'message': 'Answer saved successfully',
            'answer_id': answer.id
        }, status=status.HTTP_200_OK)


class SubmitBulkGameAnswersAPIView(APIView):
    """Submit multiple answers from a game session at once"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Submit all answers from a game session at once. Useful for saving all answers when the game ends.",
        request_body=BulkGameAnswerSerializer,
        responses={
            200: openapi.Response(
                description="Answers saved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'answers_saved': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'session_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            ),
            404: "User not found",
            400: "Invalid data"
        }
    )
    def post(self, request):
        serializer = BulkGameAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_code = serializer.validated_data['user_code']
        game_type = serializer.validated_data['game_type']
        answers_data = serializer.validated_data['answers']
        total_time = serializer.validated_data.get('total_time_seconds', 0.0)
        
        User = get_user_model()
        try:
            user = User.objects.get(unique_code=user_code)
        except User.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create all answers
        answers_created = []
        correct_count = 0
        for ans in answers_data:
            is_correct = ans.get('is_correct', False)
            if is_correct:
                correct_count += 1
            
            answer = GameAnswer.objects.create(
                player=user,
                game_type=game_type,
                question_id=ans.get('question_id', 0),
                question_text=ans.get('question_text', ''),
                selected_answer=ans.get('selected_answer', ''),
                correct_answer=ans.get('correct_answer', ''),
                is_correct=is_correct,
                time_taken_seconds=ans.get('time_taken_seconds', 0.0),
            )
            answers_created.append(answer)
        
        # Create game session record
        session = GameSession.objects.create(
            player=user,
            game_type=game_type,
            total_questions=len(answers_data),
            correct_answers=correct_count,
            total_time_seconds=total_time,
            completed=True,
            completed_at=timezone.now(),
        )
        
        return Response({
            'status': 'success',
            'message': f'Successfully saved {len(answers_created)} answers',
            'answers_saved': len(answers_created),
            'session_id': session.id,
            'score_percentage': session.score_percentage,
        }, status=status.HTTP_200_OK)


class SaveGameSessionAPIView(APIView):
    """Save a game session summary (without individual answers)"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Save a game session summary with score.",
        request_body=GameSessionSerializer,
        responses={
            200: GameSessionResponseSerializer,
            404: "User not found",
            400: "Invalid data"
        }
    )
    def post(self, request):
        serializer = GameSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_code = serializer.validated_data['user_code']
        
        User = get_user_model()
        try:
            user = User.objects.get(unique_code=user_code)
        except User.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        session = GameSession.objects.create(
            player=user,
            game_type=serializer.validated_data['game_type'],
            total_questions=serializer.validated_data['total_questions'],
            correct_answers=serializer.validated_data['correct_answers'],
            total_time_seconds=serializer.validated_data.get('total_time_seconds', 0.0),
            completed=True,
            completed_at=timezone.now(),
        )
        
        return Response({
            'status': 'success',
            'message': 'Game session saved successfully',
            'session_id': session.id,
            'score_percentage': session.score_percentage,
        }, status=status.HTTP_200_OK)


class GetPlayerGameStatsAPIView(APIView):
    """Get player's game statistics"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get player's game statistics by unique_code",
        manual_parameters=[
            openapi.Parameter('user_code', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('game_type', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
        ],
        responses={
            200: openapi.Response(
                description="Player statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_games': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_answers': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_correct': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'accuracy_percentage': openapi.Schema(type=openapi.TYPE_NUMBER),
                    }
                )
            ),
            404: "User not found"
        }
    )
    def get(self, request):
        user_code = request.query_params.get('user_code')
        game_type = request.query_params.get('game_type')
        
        if not user_code:
            return Response(
                {'status': 'error', 'message': 'user_code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        User = get_user_model()
        try:
            user = User.objects.get(unique_code=user_code)
        except User.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get answers
        answers_qs = GameAnswer.objects.filter(player=user)
        sessions_qs = GameSession.objects.filter(player=user)
        
        if game_type:
            answers_qs = answers_qs.filter(game_type=game_type)
            sessions_qs = sessions_qs.filter(game_type=game_type)
        
        total_answers = answers_qs.count()
        total_correct = answers_qs.filter(is_correct=True).count()
        total_games = sessions_qs.count()
        
        accuracy = 0
        if total_answers > 0:
            accuracy = round((total_correct / total_answers) * 100, 2)
        
        return Response({
            'status': 'success',
            'player_name': user.name,
            'total_games': total_games,
            'total_answers': total_answers,
            'total_correct': total_correct,
            'accuracy_percentage': accuracy,
        }, status=status.HTTP_200_OK)
