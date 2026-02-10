from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .models import UserFeedback

User = get_user_model()


class SubmitFeedbackAPIView(APIView):
    """
    API endpoint to submit user feedback
    
    POST /api/gameplay/feedback/
    {
        "unique_code": "ABC123456789",
        "what_works": "The quiz game was engaging...",
        "what_is_confusing": "Some instructions were unclear...",
        "what_can_be_better": "Better UI design..."
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        data = request.data
        unique_code = data.get('unique_code')
        
        if not unique_code:
            return Response(
                {'error': 'unique_code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to find the player by unique_code
        player = None
        try:
            player = User.objects.get(unique_code=unique_code)
        except User.DoesNotExist:
            pass
        
        # Create feedback
        feedback = UserFeedback.objects.create(
            player=player,
            unique_code=unique_code,
            what_works=data.get('what_works', ''),
            what_is_confusing=data.get('what_is_confusing', ''),
            what_can_be_better=data.get('what_can_be_better', ''),
        )
        
        return Response({
            'success': True,
            'message': 'Thank you for your feedback!',
            'feedback_id': feedback.id,
        }, status=status.HTTP_201_CREATED)


class GetFeedbackStatsAPIView(APIView):
    """
    API endpoint to get feedback statistics (admin use)
    
    GET /api/gameplay/feedback/stats/
    """
    permission_classes = [AllowAny]  # Change to IsAdminUser for production
    
    def get(self, request):
        total_feedbacks = UserFeedback.objects.count()
        
        # Get recent feedbacks
        recent_feedbacks = []
        for feedback in UserFeedback.objects.all()[:20]:
            recent_feedbacks.append({
                'unique_code': feedback.unique_code,
                'what_works': feedback.what_works[:100] + '...' if len(feedback.what_works) > 100 else feedback.what_works,
                'what_is_confusing': feedback.what_is_confusing[:100] + '...' if len(feedback.what_is_confusing) > 100 else feedback.what_is_confusing,
                'what_can_be_better': feedback.what_can_be_better[:100] + '...' if len(feedback.what_can_be_better) > 100 else feedback.what_can_be_better,
                'created_at': feedback.created_at.isoformat(),
            })
        
        return Response({
            'total_feedbacks': total_feedbacks,
            'recent_feedbacks': recent_feedbacks,
        })
