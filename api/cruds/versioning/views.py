"""
ViewSets for Versioning App Models
"""
from rest_framework import status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.versioning.models import AppVersion
from ..common.base import BaseModelViewSet
from .serializers import AppVersionSerializer
from ...base import success_response, error_response


class AppVersionViewSet(BaseModelViewSet):
    """CRUD operations for AppVersion model"""
    queryset = AppVersion.objects.all()
    serializer_class = AppVersionSerializer
    search_fields = ['version_number', 'platform']
    filterset_fields = ['platform', 'is_mandatory']
    ordering_fields = ['released_at', 'created_at', 'version_number']
    ordering = ['-released_at']
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest version for each platform"""
        platform = request.query_params.get('platform')
        
        if platform:
            latest_version = self.queryset.filter(platform=platform).first()
            if latest_version:
                serializer = self.get_serializer(latest_version)
                return success_response(
                    data=serializer.data,
                    message=f"Latest {platform} version retrieved successfully"
                )
            return error_response(
                message='No version found for platform', 
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Get latest for all platforms
        latest_versions = []
        for platform_choice in AppVersion.PLATFORM_CHOICES:
            platform_code = platform_choice[0]
            latest = self.queryset.filter(platform=platform_code).first()
            if latest:
                latest_versions.append(latest)
        
        serializer = self.get_serializer(latest_versions, many=True)
        return success_response(
            data=serializer.data,
            message="Latest versions retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def check_update(self, request):
        """Check if update is available for given version"""
        platform = request.query_params.get('platform')
        current_version = request.query_params.get('current_version')
        
        if not platform or not current_version:
            return error_response(
                message="platform and current_version parameters required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        latest_version = self.queryset.filter(platform=platform).first()
        
        if not latest_version:
            return error_response(
                message="No version found for platform",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        update_available = latest_version.version_number != current_version
        is_mandatory = latest_version.is_mandatory if update_available else False
        
        response_data = {
            'update_available': update_available,
            'is_mandatory': is_mandatory,
            'latest_version': latest_version.version_number,
            'current_version': current_version
        }
        
        if update_available:
            serializer = self.get_serializer(latest_version)
            response_data['version_details'] = serializer.data
        
        return success_response(
            data=response_data,
            message="Update check completed successfully"
        )