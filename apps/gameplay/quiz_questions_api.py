
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, serializers
from .models import Question

class QuizQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    number = serializers.IntegerField()
    text = serializers.CharField()
    options = serializers.ListField(child=serializers.CharField(), min_length=4, max_length=4)

class QuizQuestionsResponseSerializer(serializers.Serializer):
    questions = QuizQuestionSerializer(many=True)


class QuizQuestionsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get a random list of quiz questions with their number and options.",
        responses={200: QuizQuestionsResponseSerializer}
    )
    def get(self, request):
        import random
        questions = list(Question.objects.all())
        num_questions = min(10, len(questions))  # Return up to 10 questions
        random_questions = random.sample(questions, num_questions) if questions else []
        data = []
        for idx, q in enumerate(random_questions, start=1):
            options = getattr(q, 'options', None)
            if not options:
                options = [f"Option {i}" for i in range(1, 5)]
            data.append({
                'id': q.id,
                'number': idx,
                'text': q.text,
                'options': options,
            })
        return Response({'questions': data}, status=status.HTTP_200_OK)
