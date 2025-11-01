"""
Common permissions for API base modules
Role-based access control for User, Staff, and Admin roles
"""

from rest_framework.permissions import BasePermission
import logging

logger = logging.getLogger(__name__)


class RoleBasedPermission(BasePermission):
    """
    Custom permission class for role-based access control
    """
    required_role = None
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if self.required_role is None:
            return True
        
        return request.user.role == self.required_role


class UserRolePermission(RoleBasedPermission):
    """Permission for user role"""
    required_role = 'user'


class StaffRolePermission(RoleBasedPermission):
    """Permission for staff role"""
    required_role = 'staff'


class AdminRolePermission(RoleBasedPermission):
    """Permission for admin role"""
    required_role = 'admin'


class IsUserOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsStaffOrReadOnly(BasePermission):
    """
    Custom permission to only allow staff members to edit.
    """
    
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        return request.user.is_authenticated and request.user.is_staff


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admin users to edit.
    """
    
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        return request.user.is_authenticated and request.user.role == 'admin'