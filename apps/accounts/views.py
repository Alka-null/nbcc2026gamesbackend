from __future__ import annotations

from rest_framework import generics, permissions, response, status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    CodeLoginSerializer,
    LoginResponseSerializer,
    PlayerProfileSerializer,
    RegistrationSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new player. Organization and location are optional fields.",
        responses={201: RegistrationSerializer}
    )
    def create(self, request, *args, **kwargs):
        response_data = super().create(request, *args, **kwargs)
        return response.Response(
            {
                'message': 'Registration successful',
                'player': response_data.data,
            },
            status=status.HTTP_201_CREATED,
        )


class CodeLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Login using unique code. Works for both regular users and admin users. Returns JWT tokens and player profile.",
        request_body=CodeLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=LoginResponseSerializer,
                examples={
                    'application/json': {
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'player': {
                            'id': 1,
                            'name': 'Admin User',
                            'email': 'admin@nbcc.com',
                            'unique_code': 'BAR6HRN2',
                            'organization': '',
                            'location': '',
                            'is_staff': True,
                            'created_at': '2026-02-08T18:36:19.913Z'
                        }
                    }
                }
            ),
            400: "Invalid or inactive unique code"
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = CodeLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            player = serializer.save()
            refresh = RefreshToken.for_user(player)
            return response.Response(
                {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'player': PlayerProfileSerializer(player).data,
                }
            )
        except Exception as e:
            return response.Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProfileView(generics.RetrieveAPIView):
    serializer_class = PlayerProfileSerializer

    def get_object(self):
        return self.request.user
