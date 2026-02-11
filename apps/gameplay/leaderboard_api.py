# Ensure all imports are at the top
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status, permissions, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .quiz_stats import QuizStat
from .models import QuizResult, Challenge

# Challenge serializers and view
class ChallengeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    is_active = serializers.BooleanField()
    started_at = serializers.DateTimeField()
    ended_at = serializers.DateTimeField(allow_null=True)

class GetChallengesResponseSerializer(serializers.Serializer):
    challenges = ChallengeSerializer(many=True)

class GetChallengesAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get all challenges.",
        responses={200: GetChallengesResponseSerializer}
    )
    def get(self, request):
        challenges = Challenge.objects.all().order_by('-started_at')
        data = [
            {
                'id': c.id,
                'name': c.name,
                'is_active': c.is_active,
                'started_at': c.started_at,
                'ended_at': c.ended_at,
            } for c in challenges
        ]
        return Response({'challenges': data}, status=status.HTTP_200_OK)

# Start challenge serializers and view
class StartChallengeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)

class StartChallengeResponseSerializer(serializers.Serializer):
    challenge_id = serializers.IntegerField()
    name = serializers.CharField()
    is_active = serializers.BooleanField()
    started_at = serializers.DateTimeField()

class StartChallengeAPIView(APIView):
    permission_classes = [permissions.AllowAny]  # TODO: Change to admin only in production

    @swagger_auto_schema(
        operation_description="Start a new challenge. This will mark all previous challenges as inactive and create a new active challenge.",
        request_body=StartChallengeSerializer,
        responses={201: StartChallengeResponseSerializer}
    )
    def post(self, request):
        from django.utils import timezone
        serializer = StartChallengeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data['name']
        
        # Mark all previous challenges as inactive
        Challenge.objects.filter(is_active=True).update(is_active=False, ended_at=timezone.now())
        
        # Create new active challenge
        new_challenge = Challenge.objects.create(name=name, is_active=True)
        
        return Response({
            'challenge_id': new_challenge.id,
            'name': new_challenge.name,
            'is_active': new_challenge.is_active,
            'started_at': new_challenge.started_at,
        }, status=status.HTTP_201_CREATED)

# Game session serializers and view


class GameSessionSerializer(serializers.Serializer):
    unique_code = serializers.CharField(max_length=12)

    class Meta:
        ref_name = "LeaderboardGameSessionSerializer"

class GameSessionResponseSerializer(serializers.Serializer):
    challenge_id = serializers.IntegerField()
    challenge_name = serializers.CharField()
    current_question = serializers.IntegerField(allow_null=True)
    total_answered = serializers.IntegerField()
    total_correct = serializers.IntegerField()
    total_failed = serializers.IntegerField()

    class Meta:
        ref_name = "LeaderboardGameSessionResponseSerializer"

class GameSessionAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get the current user's game session for the latest challenge using unique_code.",
        request_body=GameSessionSerializer,
        responses={200: GameSessionResponseSerializer}
    )
    def post(self, request):
        serializer = GameSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        unique_code = serializer.validated_data['unique_code']
        User = get_user_model()
        try:
            user = User.objects.get(unique_code=unique_code)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        latest_challenge = Challenge.objects.filter(is_active=True).order_by('-started_at').first()
        if not latest_challenge:
            return Response({'detail': 'No active challenge found.'}, status=status.HTTP_404_NOT_FOUND)
        # Filter stats only for the current active challenge
        user_stats = QuizStat.objects.filter(user=user, challenge=latest_challenge)
        total_answered = user_stats.count()
        total_correct = user_stats.filter(is_correct=True).count()
        total_failed = user_stats.filter(is_correct=False).count()
        return Response({
            'challenge_id': latest_challenge.id,
            'challenge_name': latest_challenge.name,
            'current_question': total_answered,
            'total_answered': total_answered,
            'total_correct': total_correct,
            'total_failed': total_failed,
        }, status=status.HTTP_200_OK)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status, permissions, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .quiz_stats import QuizStat
from .models import QuizResult

# Serializer for adding leaderboard participant
class AddLeaderboardParticipantSerializer(serializers.Serializer):
    unique_code = serializers.CharField(max_length=12)

# Serializer for response
class AddLeaderboardParticipantResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()

class AddLeaderboardParticipantAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=AddLeaderboardParticipantSerializer,
        responses={200: AddLeaderboardParticipantResponseSerializer}
    )
    def post(self, request):
        serializer = AddLeaderboardParticipantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        unique_code = serializer.validated_data['unique_code']
        User = get_user_model()
        try:
            user = User.objects.get(unique_code=unique_code)
        except User.DoesNotExist:
            return Response({'status': 'error', 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        # Add to leaderboard participants (create QuizResult if not exists)
        quiz_result, created = QuizResult.objects.get_or_create(player=user, defaults={
            'display_name': user.name,
            'score': 0,
            'total_questions': 0,
        })
        if created:
            msg = 'User added to leaderboard participants.'
        else:
            msg = 'User already a leaderboard participant.'
        return Response({'status': 'ok', 'message': msg}, status=status.HTTP_200_OK)

class LeaderboardStatsSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.IntegerField(), required=True)

class LeaderboardStatsResponseUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    current_question = serializers.IntegerField(allow_null=True)
    total_answered = serializers.IntegerField()
    total_correct = serializers.IntegerField()
    total_failed = serializers.IntegerField()

class LeaderboardStatsResponseSerializer(serializers.Serializer):
    leaderboard = LeaderboardStatsResponseUserSerializer(many=True)

class LeaderboardStatsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=LeaderboardStatsSerializer,
        responses={200: LeaderboardStatsResponseSerializer}
    )
    def post(self, request):
        serializer = LeaderboardStatsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_ids = serializer.validated_data['user_ids']
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
        return Response({'leaderboard': stats}, status=status.HTTP_200_OK)
