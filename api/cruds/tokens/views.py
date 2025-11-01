"""
ViewSets for Tokens App Models (Read-only for CRUD API)
"""
from rest_framework import status, permissions
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone

from apps.tokens.models import MobileAppToken, APIClientToken
from ..common.base import BaseModelViewSet
from .serializers import MobileAppTokenSerializer, APIClientTokenSerializer
from ...base import success_response, error_response


class MobileAppTokenViewSet(BaseModelViewSet):
    """Read-only operations for MobileAppToken model (for reference)"""
    queryset = MobileAppToken.objects.select_related('app_version', 'created_by').all()
    serializer_class = MobileAppTokenSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    search_fields = ['name', 'role']
    filterset_fields = ['role', 'status', 'app_version']
    ordering_fields = ['created_at', 'last_used_at']
    ordering = ['-created_at']
    
    # Override to make read-only
    def create(self, request, *args, **kwargs):
        return error_response(
            message="Use admin API for token creation", 
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def update(self, request, *args, **kwargs):
        return error_response(
            message="Use admin API for token updates", 
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        return error_response(
            message="Use admin API for token deletion", 
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    @action(detail=False, methods=['get'])
    def usage_stats(self, request):
        """Get mobile token usage statistics"""
        tokens = self.get_queryset()
        
        stats = {
            'total_tokens': tokens.count(),
            'active_tokens': tokens.filter(status='active').count(),
            'suspended_tokens': tokens.filter(status='suspended').count(),
            'expired_tokens': tokens.filter(status='expired').count(),
            'tokens_by_role': {
                'admin': tokens.filter(role='admin').count(),
                'user': tokens.filter(role='user').count(),
            },
            'tokens_used_today': tokens.filter(
                last_used_at__date=timezone.now().date()
            ).count()
        }
        
        return success_response(
            data=stats,
            message="Mobile token usage statistics retrieved successfully"
        )


class APIClientTokenViewSet(BaseModelViewSet):
    """Read-only operations for APIClientToken model (for reference)"""
    queryset = APIClientToken.objects.select_related('created_by').all()
    serializer_class = APIClientTokenSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    search_fields = ['name', 'client_name', 'client_email']
    filterset_fields = ['status', 'client_organization']
    ordering_fields = ['created_at', 'last_used_at']
    ordering = ['-created_at']
    
    # Override to make read-only
    def create(self, request, *args, **kwargs):
        return error_response(
            message="Use admin API for token creation", 
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def update(self, request, *args, **kwargs):
        return error_response(
            message="Use admin API for token updates", 
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        return error_response(
            message="Use admin API for token deletion", 
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    @action(detail=False, methods=['get'])
    def usage_stats(self, request):
        """Get API client token usage statistics"""
        tokens = self.get_queryset()
        
        stats = {
            'total_tokens': tokens.count(),
            'active_tokens': tokens.filter(status='active').count(),
            'suspended_tokens': tokens.filter(status='suspended').count(),
            'expired_tokens': tokens.filter(status='expired').count(),
            'total_api_requests': sum(
                token.usage_logs.count() for token in tokens
            ),
            'tokens_used_today': tokens.filter(
                last_used_at__date=timezone.now().date()
            ).count()
        }
        
        return success_response(
            data=stats,
            message="API client token usage statistics retrieved successfully"
        )
    
    @action(detail=True, methods=['get'])
    def permissions_detail(self, request, pk=None):
        """Get detailed permissions for this token"""
        token = self.get_object()
        permissions = token.model_permissions.all()
        
        permissions_data = []
        for permission in permissions:
            permissions_data.append({
                'model_name': permission.model_name,
                'can_list': permission.can_list,
                'can_create': permission.can_create,
                'can_read': permission.can_read,
                'can_update': permission.can_update,
                'can_delete': permission.can_delete,
                'restricted_fields': permission.restricted_fields or [],
                'readonly_fields': permission.readonly_fields or [],
            })
        
        return success_response(
            data={
                'token_name': token.name,
                'client_name': token.client_name,
                'permissions': permissions_data
            },
            message="Token permissions retrieved successfully"
        )