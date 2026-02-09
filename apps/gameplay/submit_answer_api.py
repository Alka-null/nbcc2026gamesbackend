
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, serializers
from django.contrib.auth import get_user_model
from .quiz_stats import QuizStat, check_answer
from .models import Challenge

class SubmitAnswerSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=12, help_text="User's unique_code")
    question_id = serializers.IntegerField()
    answer = serializers.CharField()
    time_taken = serializers.FloatField(required=True, help_text="Time taken to answer in seconds")
    challenge_id = serializers.IntegerField(required=False, allow_null=True, help_text="Challenge ID (optional, will use active challenge if not provided)")

class SubmitAnswerResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    is_correct = serializers.BooleanField()

class SubmitAnswerAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Submit an answer for a question. user_id should be the user's unique_code.",
        request_body=SubmitAnswerSerializer,
        responses={200: SubmitAnswerResponseSerializer}
    )
    def post(self, request):
        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        unique_code = serializer.validated_data['user_id']
        question_id = serializer.validated_data['question_id']
        answer = serializer.validated_data['answer']
        time_taken = serializer.validated_data['time_taken']
        challenge_id = serializer.validated_data.get('challenge_id')
        
        User = get_user_model()
        try:
            user = User.objects.get(unique_code=unique_code)
        except User.DoesNotExist:
            return Response({'status': 'error', 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get challenge - use provided challenge_id or get active challenge
        if challenge_id:
            try:
                challenge = Challenge.objects.get(id=challenge_id)
            except Challenge.DoesNotExist:
                return Response({'status': 'error', 'message': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            challenge = Challenge.objects.filter(is_active=True).order_by('-started_at').first()
            if not challenge:
                return Response({'status': 'error', 'message': 'No active challenge found'}, status=status.HTTP_400_BAD_REQUEST)
        
        is_correct = check_answer(question_id, answer)
        QuizStat.objects.create(
            user=user, 
            challenge=challenge,
            question_id=question_id, 
            is_correct=is_correct, 
            time_taken=time_taken
        )
        return Response({'status': 'ok', 'is_correct': is_correct}, status=status.HTTP_200_OK)
