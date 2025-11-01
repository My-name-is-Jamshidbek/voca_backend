"""
Base Authentication APIs - Public Access
"""
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from apps.accounts.models import User, UserProfile
from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer
)
from ..base import success_response, error_response
import logging

logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    """
    User Registration endpoint - Public access
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="User Registration",
        description="Register a new user account",
        responses={201: UserProfileSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            user_data = UserProfileSerializer(user).data
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            
            return success_response(
                data={'user': user_data, 'tokens': tokens},
                message="User registered successfully",
                status_code=status.HTTP_201_CREATED
            )
        
        return error_response(
            message="Registration failed",
            details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with role information
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    @extend_schema(
        summary="Login",
        description="Obtain JWT tokens by providing email and password",
        responses={200: {
            "type": "object",
            "properties": {
                "access": {"type": "string"},
                "refresh": {"type": "string"},
                "user": {"type": "object"}
            }
        }}
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get user data
            email = request.data.get('email')
            try:
                user = User.objects.get(email=email)
                user_data = UserProfileSerializer(user).data
                
                # Enhance response with user data
                response.data.update({
                    'user': user_data,
                    'message': 'Login successful'
                })
                
                # Update login count
                if hasattr(user, 'profile'):
                    user.profile.login_count += 1
                    user.profile.save()
                    
            except User.DoesNotExist:
                pass
        
        return response


class LogoutView(APIView):
    """
    Logout endpoint - Blacklist the refresh token
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Logout",
        description="Logout the current user by blacklisting the refresh token",
        request={
            "type": "object",
            "properties": {
                "refresh_token": {"type": "string"}
            },
            "required": ["refresh_token"]
        },
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}},
            400: {"type": "object", "properties": {"error": {"type": "string"}}}
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return error_response(
                    message="Refresh token is required",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return success_response(
                message="Successfully logged out",
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return error_response(
                message="Invalid token",
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ChangePasswordView(APIView):
    """
    Change Password endpoint - Authenticated users only
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Change Password",
        description="Change the current user's password",
        request=ChangePasswordSerializer,
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}},
            400: {"type": "object", "properties": {"error": {"type": "string"}}}
        }
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return error_response(
                    message="Old password is incorrect",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate new password
            try:
                validate_password(serializer.validated_data['new_password'], user)
            except ValidationError as e:
                return error_response(
                    message="Password validation failed",
                    details=list(e.messages),
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return success_response(
                message="Password changed successfully",
                status_code=status.HTTP_200_OK
            )
        
        return error_response(
            message="Invalid data",
            details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )