"""
Admin Accounts API - User management for admins
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User, Permission, RolePermission
from ...base import AdminRolePermission, success_response, error_response
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class AdminUserViewSet(viewsets.ModelViewSet):
    """
    Admin API for managing all users
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, AdminRolePermission]
    
    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        """Change user role"""
        user = self.get_object()
        new_role = request.data.get('role')
        
        if new_role not in ['user', 'staff', 'admin']:
            return error_response(
                message="Invalid role",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        user.role = new_role
        user.save()
        
        return success_response(
            data={'user_id': user.id, 'new_role': new_role},
            message=f"User role changed to {new_role}"
        )
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Activate/deactivate user"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        
        status_text = "activated" if user.is_active else "deactivated"
        return success_response(
            data={'user_id': user.id, 'is_active': user.is_active},
            message=f"User {status_text} successfully"
        )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get user statistics"""
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'verified_users': User.objects.filter(is_verified=True).count(),
            'roles_breakdown': {
                'users': User.objects.filter(role='user').count(),
                'staff': User.objects.filter(role='staff').count(),
                'admins': User.objects.filter(role='admin').count(),
            },
            'recent_registrations': User.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
        }
        
        return success_response(
            data=stats,
            message="User statistics retrieved successfully"
        )


class AdminPermissionViewSet(viewsets.ModelViewSet):
    """
    Admin API for managing permissions
    """
    queryset = Permission.objects.all()
    permission_classes = [permissions.IsAuthenticated, AdminRolePermission]
    
    @action(detail=False, methods=['get'])
    def role_permissions(self, request):
        """Get permissions by role"""
        role_perms = {}
        
        for role, _ in User.ROLE_CHOICES:
            perms = RolePermission.objects.filter(role=role).select_related('permission')
            role_perms[role] = [
                {
                    'id': rp.permission.id,
                    'name': rp.permission.name,
                    'codename': rp.permission.codename,
                    'description': rp.permission.description,
                }
                for rp in perms
            ]
        
        return success_response(
            data=role_perms,
            message="Role permissions retrieved successfully"
        )
    
    @action(detail=False, methods=['post'])
    def assign_permission(self, request):
        """Assign permission to role"""
        role = request.data.get('role')
        permission_id = request.data.get('permission_id')
        
        if not role or not permission_id:
            return error_response(
                message="Role and permission_id are required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            permission = Permission.objects.get(id=permission_id)
        except Permission.DoesNotExist:
            return error_response(
                message="Permission not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        role_perm, created = RolePermission.objects.get_or_create(
            role=role,
            permission=permission
        )
        
        message = "Permission assigned" if created else "Permission already assigned"
        return success_response(
            data={'role': role, 'permission': permission.name},
            message=message
        )