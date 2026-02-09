from rest_framework import mixins, permissions, response, status, viewsets

from .models import QuizResult
from .serializers import QuizResultCreateSerializer, QuizResultSerializer


class QuizResultViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = QuizResult.objects.select_related('player')
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return QuizResultCreateSerializer
        return QuizResultSerializer

    def get_queryset(self):
        leaderboard = self.request.query_params.get('leaderboard', 'true').lower()
        if leaderboard != 'false':
            return self._leaderboard_queryset(self.request.query_params.get('limit'))

        queryset = QuizResult.objects.select_related('player')
        if self.request.user.is_authenticated:
            return queryset.filter(player=self.request.user).order_by('-created_at')

        player_name = self.request.query_params.get('player_name')
        if player_name:
            return queryset.filter(display_name__iexact=player_name).order_by('-created_at')

        return queryset.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quiz_result = serializer.save()

        read_serializer = QuizResultSerializer(quiz_result, context=self.get_serializer_context())
        leaderboard_serializer = QuizResultSerializer(
            self._leaderboard_queryset(request.query_params.get('limit')),
            many=True,
        )

        return response.Response(
            {
                'result': read_serializer.data,
                'leaderboard': leaderboard_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def _leaderboard_queryset(self, limit_param):
        queryset = QuizResult.objects.select_related('player').order_by('-score', '-created_at')
        limit_value = 10
        if limit_param:
            try:
                limit_value = max(1, min(50, int(limit_param)))
            except ValueError:
                limit_value = 10
        return queryset[:limit_value]
