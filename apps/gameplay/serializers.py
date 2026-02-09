from rest_framework import serializers

from .models import QuizResult


class QuizResultSerializer(serializers.ModelSerializer):
    player_name = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = QuizResult
        fields = ['id', 'player_name', 'score', 'total_questions', 'percentage', 'duration_seconds', 'created_at']
        read_only_fields = fields

    def get_player_name(self, obj):
        return obj.player_name

    def get_percentage(self, obj):
        if not obj.total_questions:
            return 0.0
        return round((obj.score / obj.total_questions) * 100, 2)


class QuizResultCreateSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = QuizResult
        fields = ['score', 'total_questions', 'duration_seconds', 'player_name']

    def validate(self, attrs):
        request = self.context['request']
        if not request.user.is_authenticated and not attrs.get('player_name'):
            raise serializers.ValidationError('player_name is required when not authenticated.')
        return attrs

    def create(self, validated_data):
        player_name = validated_data.pop('player_name', '')
        player = self.context['request'].user if self.context['request'].user.is_authenticated else None
        return QuizResult.objects.create(
            player=player,
            display_name=player_name,
            **validated_data,
        )
