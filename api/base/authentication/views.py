"""
Base Authentication System for Django REST Framework
Supports JWT tokens, role-based permissions, and social authentication
"""

from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
import jwt
import logging

from apps.accounts.models import User, UserDevice
from .permissions import TokenBasedAuthentication, UserRolePermission, StaffRolePermission, AdminRolePermission
from .responses import success_response, error_response

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Custom authentication error"""
    pass


class CustomTokenObtainPairSerializer(serializers.Serializer):
    """Custom JWT token serializer with user details"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    device_id = serializers.CharField(required=False, allow_blank=True)
    platform = serializers.ChoiceField(choices=UserDevice.PLATFORM_CHOICES, required=False)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if not email or not password:
            raise serializers.ValidationError('Email and password are required')
        
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled')
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Handle device registration if provided
        device_id = attrs.get('device_id')
        platform = attrs.get('platform')
        if device_id and platform:
            device, created = UserDevice.objects.get_or_create(
                user=user,
                device_id=device_id,
                defaults={'platform': platform}
            )
            if not created:
                device.last_sync = timezone.now()
                device.save(update_fields=['last_sync'])
        
        refresh = RefreshToken.for_user(user)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user,
        }


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view with enhanced response"""
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            user = data['user']
            
            response_data = {
                'tokens': {
                    'access': data['access'],
                    'refresh': data['refresh'],
                },
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': user.full_name,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'auth_provider': user.auth_provider,
                    'preferred_language': user.preferred_language,
                    'profile_picture': user.profile_picture,
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'date_joined': user.date_joined.isoformat(),
                }
            }
            
            logger.info(f"User {user.email} logged in successfully")
            return success_response(
                data=response_data,
                message="Login successful"
            )
            
        except serializers.ValidationError as e:
            logger.warning(f"Login failed: {e}")
            return error_response(
                message="Login failed",
                details=e.detail,
                status_code=status.HTTP_401_UNAUTHORIZED
            )


class RegisterSerializer(serializers.Serializer):
    """User registration serializer"""
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150, required=False, allow_blank=True)
    password = serializers.CharField(min_length=8, write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    auth_provider = serializers.ChoiceField(choices=User.AUTH_PROVIDER_CHOICES, default='email')
    auth_provider_id = serializers.CharField(required=False, allow_blank=True)
    preferred_language = serializers.CharField(max_length=10, default='en')
    device_id = serializers.CharField(required=False, allow_blank=True)
    platform = serializers.ChoiceField(choices=UserDevice.PLATFORM_CHOICES, required=False)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value
    
    def validate_username(self, value):
        if value and User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    
    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    
    def create(self, validated_data):
        # Remove password_confirm from validated_data
        validated_data.pop('password_confirm')
        device_id = validated_data.pop('device_id', None)
        platform = validated_data.pop('platform', None)
        
        # Generate username if not provided
        if not validated_data.get('username'):
            base_username = validated_data['email'].split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            validated_data['username'] = username
        
        # Create user
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        
        # Register device if provided
        if device_id and platform:
            UserDevice.objects.create(
                user=user,
                device_id=device_id,
                platform=platform
            )
        
        return user


class RegisterView(APIView):
    """User registration endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            response_data = {
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': user.full_name,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'auth_provider': user.auth_provider,
                    'preferred_language': user.preferred_language,
                    'date_joined': user.date_joined.isoformat(),
                }
            }
            
            logger.info(f"New user registered: {user.email}")
            return success_response(
                data=response_data,
                message="Registration successful",
                status_code=status.HTTP_201_CREATED
            )
            
        except serializers.ValidationError as e:
            logger.warning(f"Registration failed: {e}")
            return error_response(
                message="Registration failed",
                details=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    """Logout endpoint - blacklists refresh token"""
    permission_classes = [IsAuthenticated]
    
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
            
            logger.info(f"User {request.user.email} logged out")
            return success_response(message="Logout successful")
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return error_response(
                message="Logout failed",
                details=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ProfileView(APIView):
    """User profile management"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user profile"""
        user = request.user
        
        # Get user devices
        devices = UserDevice.objects.filter(user=user).order_by('-last_sync')
        devices_data = [
            {
                'id': str(device.id),
                'device_id': device.device_id,
                'platform': device.platform,
                'device_model': device.device_model,
                'os_version': device.os_version,
                'app_version': device.app_version,
                'last_sync': device.last_sync.isoformat() if device.last_sync else None,
                'created_at': device.created_at.isoformat(),
            }
            for device in devices
        ]
        
        profile_data = {
            'id': str(user.id),
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'auth_provider': user.auth_provider,
            'preferred_language': user.preferred_language,
            'profile_picture': user.profile_picture,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'date_joined': user.date_joined.isoformat(),
            'devices': devices_data,
        }
        
        return success_response(data=profile_data, message="Profile retrieved")
    
    def patch(self, request):
        """Update user profile"""
        user = request.user
        data = request.data
        
        # Fields that can be updated
        allowed_fields = [
            'first_name', 'last_name', 'preferred_language', 'profile_picture'
        ]
        
        updated_fields = []
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
                updated_fields.append(field)
        
        if updated_fields:
            user.save(update_fields=updated_fields)
            logger.info(f"User {user.email} updated profile: {updated_fields}")
        
        return success_response(message="Profile updated successfully")


class PasswordChangeView(APIView):
    """Change password endpoint"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')
        
        if not all([old_password, new_password, new_password_confirm]):
            return error_response(
                message="All password fields are required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != new_password_confirm:
            return error_response(
                message="New passwords do not match",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.check_password(old_password):
            return error_response(
                message="Current password is incorrect",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return error_response(
                message="Password validation failed",
                details=e.messages,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        logger.info(f"User {user.email} changed password")
        return success_response(message="Password changed successfully")


class PasswordResetTokenGenerator(PasswordResetTokenGenerator):
    """Custom password reset token generator"""
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)


password_reset_token = PasswordResetTokenGenerator()


class PasswordResetRequestView(APIView):
    """Request password reset"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return error_response(
                message="Email is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            # Don't reveal if email exists or not
            return success_response(
                message="If your email is registered, you will receive reset instructions"
            )
        
        # Generate reset token
        token = password_reset_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Create reset URL (you should customize this)
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        
        # Send email (customize email template)
        try:
            send_mail(
                subject='Password Reset Request',
                message=f'Click the link to reset your password: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info(f"Password reset email sent to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            return error_response(
                message="Failed to send reset email",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return success_response(
            message="If your email is registered, you will receive reset instructions"
        )


class PasswordResetConfirmView(APIView):
    """Confirm password reset"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')
        
        if not all([uid, token, new_password, new_password_confirm]):
            return error_response(
                message="All fields are required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != new_password_confirm:
            return error_response(
                message="Passwords do not match",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return error_response(
                message="Invalid reset link",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not password_reset_token.check_token(user, token):
            return error_response(
                message="Invalid or expired reset link",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return error_response(
                message="Password validation failed",
                details=e.messages,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        logger.info(f"Password reset completed for user {user.email}")
        return success_response(message="Password reset successful")


class TokenValidateView(APIView):
    """Validate JWT token"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return error_response(
                message="Token is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            UntypedToken(token)
            return success_response(message="Token is valid")
        except (InvalidToken, TokenError) as e:
            return error_response(
                message="Token is invalid",
                details=str(e),
                status_code=status.HTTP_401_UNAUTHORIZED
            )


class UserDeviceView(APIView):
    """Manage user devices"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user devices"""
        devices = UserDevice.objects.filter(user=request.user).order_by('-last_sync')
        devices_data = [
            {
                'id': str(device.id),
                'device_id': device.device_id,
                'platform': device.platform,
                'device_model': device.device_model,
                'os_version': device.os_version,
                'app_version': device.app_version,
                'last_sync': device.last_sync.isoformat() if device.last_sync else None,
                'created_at': device.created_at.isoformat(),
            }
            for device in devices
        ]
        
        return success_response(data=devices_data, message="Devices retrieved")
    
    def post(self, request):
        """Register a new device"""
        data = request.data
        required_fields = ['device_id', 'platform']
        
        if not all(field in data for field in required_fields):
            return error_response(
                message="device_id and platform are required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        device, created = UserDevice.objects.get_or_create(
            user=request.user,
            device_id=data['device_id'],
            defaults={
                'platform': data['platform'],
                'device_model': data.get('device_model', ''),
                'os_version': data.get('os_version', ''),
                'app_version': data.get('app_version', ''),
            }
        )
        
        if not created:
            # Update existing device
            device.platform = data['platform']
            device.device_model = data.get('device_model', device.device_model)
            device.os_version = data.get('os_version', device.os_version)
            device.app_version = data.get('app_version', device.app_version)
            device.last_sync = timezone.now()
            device.save()
        
        device_data = {
            'id': str(device.id),
            'device_id': device.device_id,
            'platform': device.platform,
            'device_model': device.device_model,
            'os_version': device.os_version,
            'app_version': device.app_version,
            'last_sync': device.last_sync.isoformat() if device.last_sync else None,
            'created_at': device.created_at.isoformat(),
        }
        
        message = "Device registered" if created else "Device updated"
        return success_response(
            data=device_data,
            message=message,
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    def delete(self, request, device_id):
        """Remove a device"""
        try:
            device = UserDevice.objects.get(id=device_id, user=request.user)
            device.delete()
            logger.info(f"Device {device_id} removed for user {request.user.email}")
            return success_response(message="Device removed successfully")
        except UserDevice.DoesNotExist:
            return error_response(
                message="Device not found",
                status_code=status.HTTP_404_NOT_FOUND
            )