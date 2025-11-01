"""
Serializers for Tokens App Models (Read-only for CRUD API)
"""
from rest_framework import serializers
from django.utils import timezone

from apps.tokens.models import MobileAppToken, APIClientToken, TokenModelPermission


class TokenModelPermissionSerializer(serializers.ModelSerializer):
    """Serializer for TokenModelPermission model"""
    model_verbose_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TokenModelPermission
        fields = [
            'id', 'model_name', 'model_verbose_name', 'can_list',
            'can_create', 'can_read', 'can_update', 'can_delete',
            'restricted_fields', 'readonly_fields', 'custom_permissions'
        ]
        read_only_fields = ['id', 'model_verbose_name']
    
    def get_model_verbose_name(self, obj):
        """Get human-readable model name"""
        model_names = {
            'User': 'Users',
            'UserDevice': 'User Devices',
            'Language': 'Languages',
            'Book': 'Books',
            'Chapter': 'Chapters',
            'DifficultyLevel': 'Difficulty Levels',
            'Word': 'Words',
            'WordTranslation': 'Word Translations',
            'WordDefinition': 'Word Definitions',
            'Collection': 'Collections',
            'CollectionWord': 'Collection Words',
            'UserProgress': 'User Progress',
            'UserSession': 'User Sessions',
            'AppVersion': 'App Versions'
        }
        return model_names.get(obj.model_name, obj.model_name)


class MobileAppTokenSerializer(serializers.ModelSerializer):
    """Serializer for MobileAppToken model (read-only for CRUD API)"""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    app_version_number = serializers.CharField(source='app_version.version_number', read_only=True)
    days_since_creation = serializers.SerializerMethodField()
    days_since_last_used = serializers.SerializerMethodField()
    
    class Meta:
        model = MobileAppToken
        fields = [
            'id', 'name', 'token', 'role', 'status', 'app_version',
            'app_version_number', 'device_info', 'last_used_at',
            'created_by', 'created_by_username', 'created_at', 'expires_at',
            'days_since_creation', 'days_since_last_used'
        ]
        read_only_fields = [
            'id', 'token', 'created_at', 'last_used_at',
            'days_since_creation', 'days_since_last_used'
        ]
    
    def get_days_since_creation(self, obj):
        """Calculate days since token creation"""
        return (timezone.now().date() - obj.created_at.date()).days
    
    def get_days_since_last_used(self, obj):
        """Calculate days since last use"""
        if not obj.last_used_at:
            return None
        return (timezone.now().date() - obj.last_used_at.date()).days


class APIClientTokenSerializer(serializers.ModelSerializer):
    """Serializer for APIClientToken model (read-only for CRUD API)"""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    model_permissions = TokenModelPermissionSerializer(many=True, read_only=True)
    total_requests = serializers.SerializerMethodField()
    permissions_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = APIClientToken
        fields = [
            'id', 'name', 'token', 'client_name', 'client_email',
            'client_organization', 'status', 'rate_limit', 'allowed_ips',
            'last_used_at', 'created_by', 'created_by_username',
            'created_at', 'expires_at', 'model_permissions',
            'total_requests', 'permissions_summary'
        ]
        read_only_fields = [
            'id', 'token', 'created_at', 'last_used_at',
            'total_requests', 'permissions_summary'
        ]
    
    def get_total_requests(self, obj):
        """Get total API requests made with this token"""
        return obj.usage_logs.count()
    
    def get_permissions_summary(self, obj):
        """Get summary of model permissions"""
        permissions = obj.model_permissions.all()
        summary = {
            'total_models': permissions.count(),
            'read_only_models': permissions.filter(
                can_list=True, can_read=True, can_create=False,
                can_update=False, can_delete=False
            ).count(),
            'full_access_models': permissions.filter(
                can_list=True, can_read=True, can_create=True,
                can_update=True, can_delete=True
            ).count()
        }
        return summary