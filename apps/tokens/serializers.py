from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import MobileAppToken, APIClientToken, TokenModelPermission, TokenUsageLog
from apps.versioning.models import AppVersion
from apps.accounts.models import User


class MobileAppTokenSerializer(serializers.ModelSerializer):
    """Serializer for Mobile App Tokens"""
    
    app_version_name = serializers.CharField(source='app_version.version_name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    token_masked = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = MobileAppToken
        fields = [
            'id', 'token', 'token_masked', 'name', 'description', 'app_version', 
            'app_version_name', 'role', 'status', 'created_by', 'created_by_username',
            'created_at', 'updated_at', 'last_used_at', 'expires_at', 'usage_count',
            'max_usage_count', 'allowed_ips', 'is_expired', 'days_until_expiry'
        ]
        read_only_fields = [
            'id', 'token', 'created_by', 'created_at', 'updated_at', 
            'last_used_at', 'usage_count'
        ]
        extra_kwargs = {
            'token': {'write_only': True},
        }
    
    def get_token_masked(self, obj):
        """Return masked token for security"""
        if obj.token:
            return f"{obj.token[:8]}...{obj.token[-8:]}"
        return None
    
    def get_is_expired(self, obj):
        """Check if token is expired"""
        return not obj.is_valid()
    
    def get_days_until_expiry(self, obj):
        """Calculate days until expiry"""
        if obj.expires_at:
            from datetime import datetime
            delta = obj.expires_at - datetime.now()
            return delta.days if delta.days > 0 else 0
        return None
    
    def validate_expires_at(self, value):
        """Validate expiry date is in future"""
        if value:
            from datetime import datetime
            if value <= datetime.now():
                raise serializers.ValidationError("Expiry date must be in the future")
        return value
    
    def validate_max_usage_count(self, value):
        """Validate max usage count"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Max usage count must be positive")
        return value


class MobileAppTokenCreateSerializer(MobileAppTokenSerializer):
    """Serializer for creating Mobile App Tokens with token in response"""
    
    class Meta(MobileAppTokenSerializer.Meta):
        extra_kwargs = {}  # Remove write_only from token field
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TokenModelPermissionSerializer(serializers.ModelSerializer):
    """Serializer for Token Model Permissions"""
    
    permissions_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = TokenModelPermission
        fields = [
            'id', 'model_name', 'can_create', 'can_read', 'can_update', 
            'can_delete', 'can_list', 'can_bulk_create', 'can_bulk_update',
            'can_bulk_delete', 'restricted_fields', 'readonly_fields',
            'permissions_summary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_permissions_summary(self, obj):
        """Get human-readable permissions summary"""
        perms = []
        if obj.can_create: perms.append('Create')
        if obj.can_read: perms.append('Read')
        if obj.can_update: perms.append('Update')
        if obj.can_delete: perms.append('Delete')
        if obj.can_list: perms.append('List')
        
        bulk_perms = []
        if obj.can_bulk_create: bulk_perms.append('Bulk Create')
        if obj.can_bulk_update: bulk_perms.append('Bulk Update')
        if obj.can_bulk_delete: bulk_perms.append('Bulk Delete')
        
        result = ', '.join(perms) if perms else 'No permissions'
        if bulk_perms:
            result += f' + {", ".join(bulk_perms)}'
        
        return result


class APIClientTokenSerializer(serializers.ModelSerializer):
    """Serializer for API Client Tokens"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    token_masked = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    model_permissions = TokenModelPermissionSerializer(many=True, read_only=True)
    permissions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = APIClientToken
        fields = [
            'id', 'token', 'token_masked', 'name', 'description', 'client_name',
            'client_email', 'client_organization', 'status', 'created_by',
            'created_by_username', 'created_at', 'updated_at', 'last_used_at',
            'expires_at', 'usage_count', 'max_usage_count', 'rate_limit_per_hour',
            'rate_limit_per_day', 'allowed_ips', 'allowed_endpoints', 'model_permissions',
            'permissions_count', 'is_expired', 'days_until_expiry'
        ]
        read_only_fields = [
            'id', 'token', 'created_by', 'created_at', 'updated_at',
            'last_used_at', 'usage_count'
        ]
        extra_kwargs = {
            'token': {'write_only': True},
            'client_email': {'validators': [UniqueValidator(queryset=APIClientToken.objects.all())]},
        }
    
    def get_token_masked(self, obj):
        """Return masked token for security"""
        if obj.token:
            return f"{obj.token[:8]}...{obj.token[-8:]}"
        return None
    
    def get_is_expired(self, obj):
        """Check if token is expired"""
        return not obj.is_valid()
    
    def get_days_until_expiry(self, obj):
        """Calculate days until expiry"""
        if obj.expires_at:
            from datetime import datetime
            delta = obj.expires_at - datetime.now()
            return delta.days if delta.days > 0 else 0
        return None
    
    def get_permissions_count(self, obj):
        """Get count of model permissions"""
        return obj.model_permissions.count()
    
    def validate_expires_at(self, value):
        """Validate expiry date is in future"""
        if value:
            from datetime import datetime
            if value <= datetime.now():
                raise serializers.ValidationError("Expiry date must be in the future")
        return value
    
    def validate_rate_limit_per_hour(self, value):
        """Validate hourly rate limit"""
        if value <= 0:
            raise serializers.ValidationError("Hourly rate limit must be positive")
        return value
    
    def validate_rate_limit_per_day(self, value):
        """Validate daily rate limit"""
        if value <= 0:
            raise serializers.ValidationError("Daily rate limit must be positive")
        return value


class APIClientTokenCreateSerializer(APIClientTokenSerializer):
    """Serializer for creating API Client Tokens with token in response"""
    
    permissions_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="List of model permissions to create"
    )
    
    class Meta(APIClientTokenSerializer.Meta):
        extra_kwargs = {
            'client_email': {'validators': [UniqueValidator(queryset=APIClientToken.objects.all())]},
        }  # Remove write_only from token field
    
    def create(self, validated_data):
        permissions_data = validated_data.pop('permissions_data', [])
        validated_data['created_by'] = self.context['request'].user
        
        token = super().create(validated_data)
        
        # Create model permissions
        for perm_data in permissions_data:
            TokenModelPermission.objects.create(token=token, **perm_data)
        
        return token


class APIClientTokenUpdateSerializer(APIClientTokenSerializer):
    """Serializer for updating API Client Tokens"""
    
    permissions_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="List of model permissions to update/create"
    )
    
    class Meta(APIClientTokenSerializer.Meta):
        pass
    
    def update(self, instance, validated_data):
        permissions_data = validated_data.pop('permissions_data', None)
        
        token = super().update(instance, validated_data)
        
        # Update model permissions if provided
        if permissions_data is not None:
            # Delete existing permissions
            token.model_permissions.all().delete()
            
            # Create new permissions
            for perm_data in permissions_data:
                TokenModelPermission.objects.create(token=token, **perm_data)
        
        return token


class TokenUsageLogSerializer(serializers.ModelSerializer):
    """Serializer for Token Usage Logs"""
    
    class Meta:
        model = TokenUsageLog
        fields = [
            'id', 'token_type', 'token_id', 'token_name', 'endpoint',
            'method', 'ip_address', 'user_agent', 'status_code',
            'response_time_ms', 'request_data_size', 'response_data_size',
            'timestamp'
        ]
        read_only_fields = '__all__'  # All fields are read-only


class TokenStatsSerializer(serializers.Serializer):
    """Serializer for token statistics"""
    
    total_mobile_tokens = serializers.IntegerField()
    active_mobile_tokens = serializers.IntegerField()
    total_api_tokens = serializers.IntegerField()
    active_api_tokens = serializers.IntegerField()
    total_usage_today = serializers.IntegerField()
    total_usage_this_week = serializers.IntegerField()
    total_usage_this_month = serializers.IntegerField()
    most_used_endpoints = serializers.ListField()
    recent_activity = serializers.ListField()


class TokenValidationSerializer(serializers.Serializer):
    """Serializer for token validation"""
    
    token = serializers.CharField(max_length=64, required=True)
    endpoint = serializers.CharField(max_length=200, required=False)
    method = serializers.CharField(max_length=10, required=False)
    ip_address = serializers.IPAddressField(required=False)
    
    def validate_token(self, value):
        """Validate token format"""
        if not (value.startswith('mob_') or value.startswith('api_')):
            raise serializers.ValidationError("Invalid token format")
        return value


class BulkTokenActionSerializer(serializers.Serializer):
    """Serializer for bulk token actions"""
    
    ACTION_CHOICES = [
        ('activate', 'Activate'),
        ('deactivate', 'Deactivate'),
        ('revoke', 'Revoke'),
        ('delete', 'Delete'),
    ]
    
    token_ids = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text="List of token IDs to perform action on"
    )
    action = serializers.ChoiceField(choices=ACTION_CHOICES, required=True)
    reason = serializers.CharField(max_length=500, required=False, help_text="Reason for the action")
    
    def validate_token_ids(self, value):
        """Validate token IDs"""
        if not value:
            raise serializers.ValidationError("At least one token ID is required")
        return value