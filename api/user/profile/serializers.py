"""
User Profile Serializers
Handles serialization of user profile data for Flutter app
"""

from rest_framework import serializers
from apps.accounts.models import User, UserProfile, UserDevice
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class UserDeviceSerializer(serializers.ModelSerializer):
    """
    Serializer for User Device
    
    Fields:
        - id: Device unique identifier
        - device_id: Device hardware identifier
        - device_name: Name of the device (e.g., "iPhone 14 Pro")
        - platform: Device platform (ios, android, web, desktop)
        - os_version: Operating system version
        - app_version: Installed app version
        - is_active: Whether device is currently active
        - last_sync: Last synchronization timestamp
        - created_at: Device registration timestamp
    
    Example:
        {
            "id": "device-123",
            "device_id": "hardware-id-xyz",
            "device_name": "iPhone 14 Pro",
            "platform": "ios",
            "os_version": "17.0",
            "app_version": "1.0.0",
            "is_active": true,
            "last_sync": "2024-11-01T10:30:00Z",
            "created_at": "2024-10-15T14:20:00Z"
        }
    """
    
    class Meta:
        model = UserDevice
        fields = [
            'id', 'device_id', 'device_name', 'platform', 
            'os_version', 'app_version', 'is_active', 
            'last_sync', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_sync']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for User Profile
    
    Fields:
        - id: User unique identifier
        - profile_id: User profile unique identifier
        - first_name: User's first name
        - last_name: User's last name
        - email: User's email address
        - phone: User's phone number
        - bio: User's biography
        - avatar_url: URL to user's avatar image
        - birth_date: User's date of birth
        - preferred_language: Primary learning language
        - secondary_languages: Secondary learning languages (comma-separated)
        - timezone: User's timezone
        - theme: UI theme preference (light, dark)
        - notifications_enabled: Whether notifications are enabled
        - email_verified: Whether email is verified
        - phone_verified: Whether phone is verified
        - created_at: Account creation timestamp
        - updated_at: Last profile update timestamp
    
    Example:
        {
            "id": "user-123",
            "profile_id": "profile-456",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "bio": "Language enthusiast",
            "avatar_url": "https://example.com/avatars/user-123.jpg",
            "birth_date": "1990-01-15",
            "preferred_language": "English",
            "secondary_languages": "German,Spanish",
            "timezone": "America/New_York",
            "theme": "dark",
            "notifications_enabled": true,
            "email_verified": true,
            "phone_verified": false,
            "created_at": "2024-10-01T12:00:00Z",
            "updated_at": "2024-11-01T15:30:00Z"
        }
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'profile_id', 'first_name', 'last_name', 
            'email', 'phone', 'bio', 'avatar_url', 
            'birth_date', 'preferred_language', 'secondary_languages',
            'timezone', 'theme', 'notifications_enabled',
            'email_verified', 'phone_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'profile_id', 'created_at', 'updated_at']


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for User Details with Profile Information
    
    Fields:
        - id: User unique identifier
        - email: User's email address
        - is_staff: Whether user is staff member
        - is_active: Whether user account is active
        - role: User role (user, staff, admin)
        - profile: User profile details (nested UserProfileSerializer)
        - devices: User devices list (nested UserDeviceSerializer)
        - created_at: Account creation timestamp
        - updated_at: Last update timestamp
    
    Example:
        {
            "id": "user-123",
            "email": "john@example.com",
            "is_staff": false,
            "is_active": true,
            "role": "user",
            "profile": {
                "id": "profile-456",
                "first_name": "John",
                "last_name": "Doe",
                ...
            },
            "devices": [
                {
                    "id": "device-123",
                    "device_name": "iPhone 14 Pro",
                    ...
                }
            ],
            "created_at": "2024-10-01T12:00:00Z",
            "updated_at": "2024-11-01T15:30:00Z"
        }
    """
    
    profile = UserProfileSerializer(read_only=True)
    devices = UserDeviceSerializer(many=True, read_only=True, source='user_devices')
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'is_staff', 'is_active', 
            'role', 'profile', 'devices', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for Updating User Profile
    
    Editable Fields:
        - first_name: User's first name (max 150 characters)
        - last_name: User's last name (max 150 characters)
        - phone: Phone number
        - bio: Biography (max 500 characters)
        - avatar_url: Avatar image URL
        - birth_date: Date of birth (YYYY-MM-DD)
        - preferred_language: Primary learning language
        - secondary_languages: Secondary languages (comma-separated)
        - timezone: User's timezone (e.g., America/New_York)
        - theme: UI theme (light, dark)
        - notifications_enabled: Enable/disable notifications
    
    Example Request:
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "phone": "+1234567890",
            "bio": "German language learner",
            "birth_date": "1992-05-20",
            "preferred_language": "German",
            "secondary_languages": "French,Spanish",
            "timezone": "Europe/Berlin",
            "theme": "dark",
            "notifications_enabled": true
        }
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'phone', 'bio', 
            'avatar_url', 'birth_date', 'preferred_language',
            'secondary_languages', 'timezone', 'theme',
            'notifications_enabled'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for Password Change
    
    Fields:
        - old_password: Current password (required, non-empty)
        - new_password: New password (min 8 chars, must be strong)
        - confirm_password: Confirm new password (must match new_password)
    
    Default Values:
        - Password minimum length: 8 characters
        - Password complexity: At least one digit, one letter, one symbol
    
    Example Request:
        {
            "old_password": "CurrentPassword123!",
            "new_password": "NewPassword456@",
            "confirm_password": "NewPassword456@"
        }
    
    Example Response:
        {
            "success": true,
            "message": "Password changed successfully",
            "data": null
        }
    """
    
    old_password = serializers.CharField(
        write_only=True, 
        required=True,
        min_length=1,
        help_text="User's current password"
    )
    new_password = serializers.CharField(
        write_only=True, 
        required=True,
        min_length=8,
        help_text="New password (minimum 8 characters)"
    )
    confirm_password = serializers.CharField(
        write_only=True, 
        required=True,
        help_text="Confirm new password"
    )
    
    def validate_new_password(self, value):
        """Validate new password strength"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate(self, data):
        """Validate passwords match"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError(
                {"new_password": "New password must be different from old password"}
            )
        return data


class UserStatisticsSerializer(serializers.Serializer):
    """
    Serializer for User Learning Statistics
    
    Fields:
        - total_words_available: Total words in the system
        - words_learned: Number of fully learned words (mastery >= 3)
        - words_in_progress: Words currently being learned (mastery 1-2)
        - words_not_started: Words not yet started
        - review_due: Words due for review today
        - learning_percentage: Learning progress percentage (0-100)
        - current_streak: Current consecutive days learning
        - last_session_date: Last learning session date
        - total_sessions: Total learning sessions completed
        - total_study_time: Total study time in minutes
    
    Example Response:
        {
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
    """
    
    total_words_available = serializers.IntegerField()
    words_learned = serializers.IntegerField()
    words_in_progress = serializers.IntegerField()
    words_not_started = serializers.IntegerField()
    review_due = serializers.IntegerField()
    learning_percentage = serializers.FloatField()
    current_streak = serializers.IntegerField()
    last_session_date = serializers.DateTimeField(allow_null=True)
    total_sessions = serializers.IntegerField()
    total_study_time = serializers.IntegerField()
