from __future__ import annotations

import logging
import traceback
from datetime import datetime

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

# Configure logger for login tracking
logger = logging.getLogger('accounts.login')


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

    def _get_client_ip(self, request):
        """Extract client IP from request headers."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')

    def _get_request_context(self, request):
        """Build context dict for logging."""
        return {
            'ip': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', 'unknown')[:200],
            'timestamp': datetime.now().isoformat(),
            'path': request.path,
            'method': request.method,
        }

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
        ctx = self._get_request_context(request)
        unique_code = request.data.get('unique_code', '')
        masked_code = unique_code[:3] + '***' if len(unique_code) > 3 else '***'
        
        logger.info(
            f"LOGIN_ATTEMPT | code={masked_code} | ip={ctx['ip']} | "
            f"user_agent={ctx['user_agent'][:50]} | timestamp={ctx['timestamp']}"
        )
        
        try:
            # Step 1: Validate serializer
            logger.debug(f"LOGIN_STEP_1 | Validating serializer | code={masked_code}")
            serializer = CodeLoginSerializer(data=request.data)
            
            if not serializer.is_valid():
                errors = serializer.errors
                logger.warning(
                    f"LOGIN_VALIDATION_FAILED | code={masked_code} | ip={ctx['ip']} | "
                    f"errors={errors} | timestamp={ctx['timestamp']}"
                )
                return response.Response(
                    {'detail': 'Invalid request data', 'errors': errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Step 2: Authenticate and get player
            logger.debug(f"LOGIN_STEP_2 | Looking up player | code={masked_code}")
            player = serializer.save()
            
            if not player:
                logger.warning(
                    f"LOGIN_PLAYER_NOT_FOUND | code={masked_code} | ip={ctx['ip']} | "
                    f"timestamp={ctx['timestamp']}"
                )
                return response.Response(
                    {'detail': 'Invalid or inactive unique code'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Step 3: Generate JWT tokens
            logger.debug(f"LOGIN_STEP_3 | Generating tokens | player_id={player.id}")
            refresh = RefreshToken.for_user(player)
            
            # Step 4: Success - log and return
            logger.info(
                f"LOGIN_SUCCESS | player_id={player.id} | name={player.name} | "
                f"code={masked_code} | ip={ctx['ip']} | is_staff={player.is_staff} | "
                f"timestamp={ctx['timestamp']}"
            )
            
            return response.Response(
                {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'player': PlayerProfileSerializer(player).data,
                }
            )
            
        except serializer.ValidationError as ve:
            logger.warning(
                f"LOGIN_VALIDATION_ERROR | code={masked_code} | ip={ctx['ip']} | "
                f"error={str(ve)} | timestamp={ctx['timestamp']}"
            )
            return response.Response(
                {'detail': str(ve)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            # Log full traceback for unexpected errors
            tb = traceback.format_exc()
            logger.error(
                f"LOGIN_ERROR | code={masked_code} | ip={ctx['ip']} | "
                f"error_type={type(e).__name__} | error={str(e)} | "
                f"timestamp={ctx['timestamp']}\n{tb}"
            )
            return response.Response(
                {'detail': 'Login failed. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProfileView(generics.RetrieveAPIView):
    serializer_class = PlayerProfileSerializer

    def get_object(self):
        return self.request.user
