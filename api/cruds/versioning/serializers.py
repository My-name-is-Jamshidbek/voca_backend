"""
Serializers for Versioning App Models
"""
from rest_framework import serializers
from django.utils import timezone

from apps.versioning.models import AppVersion


class AppVersionSerializer(serializers.ModelSerializer):
    """Serializer for AppVersion model"""
    is_latest = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = AppVersion
        fields = [
            'id', 'version_number', 'version_code', 'platform',
            'release_notes', 'download_url', 'minimum_os_version',
            'is_mandatory', 'is_beta', 'released_at', 'created_at',
            'updated_at', 'is_latest'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_latest']
    
    def get_is_latest(self, obj):
        """Check if this is the latest version for the platform"""
        latest = AppVersion.objects.filter(platform=obj.platform).first()
        return latest and latest.id == obj.id
    
    def get_download_url(self, obj):
        """Generate platform-specific download URL"""
        if obj.platform == 'android':
            return f"https://play.google.com/store/apps/details?id=com.vocaapp.mobile"
        elif obj.platform == 'ios':
            return f"https://apps.apple.com/app/vocaapp/id123456789"
        elif obj.platform == 'web':
            return f"https://app.vocaapp.com/"
        return obj.download_url