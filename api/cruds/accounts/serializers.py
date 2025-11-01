"""
Serializers for Accounts App Models
"""
from rest_framework import serializers
from django.utils import timezone

from apps.accounts.models import User, UserDevice


class UserDeviceSerializer(serializers.ModelSerializer):
    """Serializer for UserDevice model"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserDevice
        fields = [
            'id', 'device_id', 'platform', 'device_model', 'os_version',
            'app_version', 'timezone', 'language', 'push_token',
            'is_active', 'last_sync', 'created_at', 'updated_at',
            'user', 'user_username'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_username']
    
    def create(self, validated_data):
        # Remove device_id duplicates for same user
        user = validated_data.get('user')
        device_id = validated_data.get('device_id')
        
        # Deactivate existing device with same device_id
        UserDevice.objects.filter(
            user=user, device_id=device_id
        ).update(is_active=False)
        
        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.SerializerMethodField()
    total_devices = serializers.SerializerMethodField()
    last_active = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'is_active', 'is_staff', 'date_joined',
            'last_login', 'total_devices', 'last_active'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'full_name',
            'total_devices', 'last_active'
        ]
    
    def get_full_name(self, obj):
        """Get user's full name"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username
    
    def get_total_devices(self, obj):
        """Get total active devices for user"""
        return obj.devices.filter(is_active=True).count()
    
    def get_last_active(self, obj):
        """Get last active datetime (last login or device sync)"""
        last_login = obj.last_login
        last_device_sync = obj.devices.filter(
            is_active=True
        ).order_by('-last_sync').first()
        
        if last_device_sync and last_device_sync.last_sync:
            if not last_login:
                return last_device_sync.last_sync
            return max(last_login, last_device_sync.last_sync)
        
        return last_login