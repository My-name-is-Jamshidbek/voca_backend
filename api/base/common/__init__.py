"""
Common module initialization for API base common utilities
"""

from .views import (
    RoleBasedPermission,
    UserRolePermission,
    StaffRolePermission,
    AdminRolePermission,
    BaseAPIView,
    ResponseMixin,
    APIRootView,
    success_response,
    error_response,
)

from .permissions import (
    IsUserOrReadOnly,
    IsStaffOrReadOnly,
    IsAdminOrReadOnly,
)

from .responses import (
    validation_error_response,
    permission_denied_response,
    not_found_response,
    unauthorized_response,
)

__all__ = [
    'RoleBasedPermission',
    'UserRolePermission', 
    'StaffRolePermission',
    'AdminRolePermission',
    'BaseAPIView',
    'ResponseMixin',
    'APIRootView',
    'success_response',
    'error_response',
    'IsUserOrReadOnly',
    'IsStaffOrReadOnly',
    'IsAdminOrReadOnly',
    'validation_error_response',
    'permission_denied_response',
    'not_found_response',
    'unauthorized_response',
]