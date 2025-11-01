"""
ViewSets for Accounts App Models
"""
from rest_framework import status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.accounts.models import User, UserDevice
from ..common.base import BaseModelViewSet
from .serializers import UserSerializer, UserDeviceSerializer
from ...base import success_response, error_response


class UserViewSet(BaseModelViewSet):
    """CRUD operations for User model"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    
    def get_queryset(self):
        """Filter queryset based on token permissions and user role"""
        queryset = super().get_queryset()
        
        # If mobile token with user role, only show own profile
        if hasattr(self.request, 'token_data'):
            token_data = self.request.token_data
            if token_data.get('token_type') == 'mobile' and token_data.get('role') == 'user':
                return queryset.filter(id=self.request.user.id)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def devices(self, request, pk=None):
        """Get all devices for this user"""
        user = self.get_object()
        devices = user.devices.filter(is_active=True)
        serializer = UserDeviceSerializer(devices, many=True)
        return success_response(
            data=serializer.data,
            message="User devices retrieved successfully"
        )
    
    @action(detail=True, methods=['get'])
    def profile_stats(self, request, pk=None):
        """Get user profile statistics"""
        user = self.get_object()
        
        # Import here to avoid circular imports
        from apps.progress.models import UserProgress, UserSession
        
        stats = {
            'total_words_learned': UserProgress.objects.filter(
                user=user, status='learned'
            ).count(),
            'total_words_learning': UserProgress.objects.filter(
                user=user, status='learning'
            ).count(),
            'total_study_sessions': UserSession.objects.filter(user=user).count(),
            'total_study_time_minutes': sum(
                session.total_time_minutes 
                for session in UserSession.objects.filter(user=user)
            ),
            'active_devices': user.devices.filter(is_active=True).count(),
            'member_since': user.date_joined.strftime('%B %Y'),
        }
        
        return success_response(
            data=stats,
            message="User profile statistics retrieved successfully"
        )


class UserDeviceViewSet(BaseModelViewSet):
    """CRUD operations for UserDevice model"""
    queryset = UserDevice.objects.select_related('user').all()
    serializer_class = UserDeviceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['device_id', 'platform', 'device_model']
    filterset_fields = ['platform', 'user', 'is_active']
    ordering_fields = ['created_at', 'last_sync']
    ordering = ['-last_sync']
    
    def get_queryset(self):
        """Filter devices based on user permissions"""
        queryset = super().get_queryset()
        
        # Users can only see their own devices
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def sync_data(self, request, pk=None):
        """Update device sync timestamp"""
        device = self.get_object()
        device.update_sync()
        
        return success_response(
            data={'last_sync': device.last_sync},
            message="Device sync updated successfully"
        )
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a device"""
        device = self.get_object()
        device.is_active = False
        device.save()
        
        return success_response(
            message="Device deactivated successfully"
        )