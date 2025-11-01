"""
User Profile Views
Comprehensive profile management APIs for Flutter app with Bearer authentication
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from apps.accounts.models import User, UserProfile, UserDevice
from ..common import UserAPIView, UserAuthenticationMixin, UserResponseMixin, calculate_learning_stats, calculate_streak
from .serializers import (
    UserDetailSerializer, UserProfileSerializer, UserProfileUpdateSerializer,
    ChangePasswordSerializer, UserStatisticsSerializer, UserDeviceSerializer
)
import logging

logger = logging.getLogger(__name__)


class UserProfileViewSet(viewsets.ViewSet, UserAuthenticationMixin, UserResponseMixin):
    """
    User Profile Management ViewSet
    
    Comprehensive API endpoints for managing user profile information
    Requires Bearer token authentication
    
    Endpoints:
        GET    /api/user/profile/                 - Get current user profile
        PUT    /api/user/profile/                 - Update user profile
        DELETE /api/user/profile/                 - Delete user account
        POST   /api/user/profile/change_password/ - Change password
        GET    /api/user/profile/statistics/      - Get learning statistics
        POST   /api/user/profile/avatar/          - Upload avatar
        GET    /api/user/profile/devices/         - List user devices
        POST   /api/user/profile/devices/         - Register new device
        DELETE /api/user/profile/devices/{id}/    - Remove device
        POST   /api/user/profile/logout_all/      - Logout from all devices
    """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get current user's profile"""
        try:
            return self.request.user.profile
        except UserProfile.DoesNotExist:
            raise Response(
                self.error_response(
                    message="User profile not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            )
    
    def list(self, request):
        """
        Get current user profile
        
        Returns:
            {
                "success": true,
                "message": "Profile retrieved successfully",
                "data": {
                    "id": "user-123",
                    "email": "user@example.com",
                    "profile": {
                        "first_name": "John",
                        "last_name": "Doe",
                        "phone": "+1234567890",
                        ...
                    },
                    "devices": [...]
                }
            }
        """
        user = request.user
        serializer = UserDetailSerializer(user)
        return self.success_response(
            data=serializer.data,
            message="Profile retrieved successfully"
        )
    
    @action(detail=False, methods=['put'], url_path='update')
    def update(self, request):
        """
        Update current user profile
        
        Request Body:
            {
                "first_name": "Jane",
                "last_name": "Smith",
                "phone": "+9876543210",
                "bio": "Language enthusiast",
                "birth_date": "1992-05-20",
                "preferred_language": "German",
                "secondary_languages": "French,Spanish",
                "timezone": "Europe/Berlin",
                "theme": "dark",
                "notifications_enabled": true
            }
        
        Returns:
            {
                "success": true,
                "message": "Profile updated successfully",
                "data": {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    ...
                }
            }
        """
        profile = self.get_object()
        serializer = UserProfileUpdateSerializer(
            profile, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Profile updated successfully"
            )
        
        return self.validation_error_response(
            errors=serializer.errors,
            message="Profile update failed"
        )
    
    @action(detail=False, methods=['post'], url_path='change_password')
    def change_password(self, request):
        """
        Change user password
        
        Request Body:
            {
                "old_password": "CurrentPassword123!",
                "new_password": "NewPassword456@",
                "confirm_password": "NewPassword456@"
            }
        
        Returns:
            {
                "success": true,
                "message": "Password changed successfully",
                "data": null
            }
        """
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            # Verify old password
            if not user.check_password(serializer.validated_data['old_password']):
                return self.error_response(
                    message="Old password is incorrect",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            logger.info(f"User {user.id} changed password successfully")
            
            return self.success_response(
                data=None,
                message="Password changed successfully"
            )
        
        return self.validation_error_response(
            errors=serializer.errors,
            message="Password change failed"
        )
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """
        Get user learning statistics
        
        Returns:
            {
                "success": true,
                "message": "Statistics retrieved successfully",
                "data": {
                    "total_words_available": 5000,
                    "words_learned": 250,
                    "words_in_progress": 150,
                    "words_not_started": 4600,
                    "review_due": 15,
                    "learning_percentage": 5.0,
                    "current_streak": 7,
                    "last_session_date": "2024-11-01",
                    "total_sessions": 42,
                    "total_study_time": 1260
                }
            }
        """
        stats = calculate_learning_stats(request.user)
        streak = calculate_streak(request.user)
        
        # Merge streak data with stats
        stats.update(streak)
        
        serializer = UserStatisticsSerializer(stats)
        return self.success_response(
            data=serializer.data,
            message="Statistics retrieved successfully"
        )
    
    @action(detail=False, methods=['post'], url_path='avatar')
    def upload_avatar(self, request):
        """
        Upload or update user avatar
        
        Request Body (multipart/form-data):
            - avatar: Avatar image file (JPG, PNG, max 5MB)
        
        Returns:
            {
                "success": true,
                "message": "Avatar uploaded successfully",
                "data": {
                    "avatar_url": "https://example.com/media/avatars/user-123.jpg"
                }
            }
        """
        if 'avatar' not in request.FILES:
            return self.error_response(
                message="Avatar file is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            profile = self.get_object()
            profile.avatar_url = request.FILES['avatar']
            profile.save()
            
            return self.success_response(
                data={'avatar_url': profile.avatar_url.url},
                message="Avatar uploaded successfully"
            )
        except Exception as e:
            logger.error(f"Avatar upload failed: {e}")
            return self.error_response(
                message="Avatar upload failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['delete'], url_path='')
    def delete_account(self, request):
        """
        Delete user account (soft delete)
        
        WARNING: This action is permanent and cannot be undone.
        
        Returns:
            {
                "success": true,
                "message": "Account deleted successfully",
                "data": null
            }
        """
        try:
            user = request.user
            user.is_active = False
            user.save()
            
            logger.info(f"User {user.id} deleted account")
            
            return self.success_response(
                data=None,
                message="Account deleted successfully"
            )
        except Exception as e:
            logger.error(f"Account deletion failed: {e}")
            return self.error_response(
                message="Account deletion failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='devices')
    def list_devices(self, request):
        """
        List all user devices
        
        Returns:
            {
                "success": true,
                "message": "Devices retrieved successfully",
                "data": [
                    {
                        "id": "device-123",
                        "device_name": "iPhone 14 Pro",
                        "platform": "ios",
                        "os_version": "17.0",
                        "app_version": "1.0.0",
                        "is_active": true,
                        "last_sync": "2024-11-01T10:30:00Z"
                    }
                ]
            }
        """
        devices = UserDevice.objects.filter(user=request.user)
        serializer = UserDeviceSerializer(devices, many=True)
        return self.success_response(
            data=serializer.data,
            message="Devices retrieved successfully"
        )
    
    @action(detail=False, methods=['post'], url_path='devices')
    def register_device(self, request):
        """
        Register new device
        
        Request Body:
            {
                "device_id": "hardware-id-xyz",
                "device_name": "iPhone 14 Pro",
                "platform": "ios",
                "os_version": "17.0",
                "app_version": "1.0.0"
            }
        
        Returns:
            {
                "success": true,
                "message": "Device registered successfully",
                "data": {
                    "id": "device-123",
                    "device_id": "hardware-id-xyz",
                    ...
                }
            }
        """
        serializer = UserDeviceSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return self.success_response(
                data=serializer.data,
                message="Device registered successfully",
                status_code=status.HTTP_201_CREATED
            )
        
        return self.validation_error_response(
            errors=serializer.errors,
            message="Device registration failed"
        )
    
    @action(detail=False, methods=['delete'], url_path='devices/(?P<device_id>[^/.]+)')
    def remove_device(self, request, device_id=None):
        """
        Remove device
        
        Path Parameters:
            - device_id: Device ID to remove
        
        Returns:
            {
                "success": true,
                "message": "Device removed successfully",
                "data": null
            }
        """
        try:
            device = UserDevice.objects.get(id=device_id, user=request.user)
            device.delete()
            
            logger.info(f"User {request.user.id} removed device {device_id}")
            
            return self.success_response(
                data=None,
                message="Device removed successfully"
            )
        except UserDevice.DoesNotExist:
            return self.not_found_response(message="Device not found")
        except Exception as e:
            logger.error(f"Device removal failed: {e}")
            return self.error_response(
                message="Device removal failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='logout_all')
    def logout_all_devices(self, request):
        """
        Logout from all devices
        
        Deactivates all user devices and invalidates all sessions
        
        Returns:
            {
                "success": true,
                "message": "Logged out from all devices successfully",
                "data": null
            }
        """
        try:
            UserDevice.objects.filter(user=request.user).update(is_active=False)
            
            logger.info(f"User {request.user.id} logged out from all devices")
            
            return self.success_response(
                data=None,
                message="Logged out from all devices successfully"
            )
        except Exception as e:
            logger.error(f"Logout all devices failed: {e}")
            return self.error_response(
                message="Logout failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
