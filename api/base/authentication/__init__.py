"""
Authentication module initialization
"""

from .views import (
    CustomTokenObtainPairView,
    RegisterView,
    LogoutView,
    ProfileView,
    PasswordChangeView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    TokenValidateView,
    UserDeviceView,
)

from .permissions import (
    TokenBasedAuthentication,
    RoleBasedPermission,
    UserRolePermission,
    StaffRolePermission,
    AdminRolePermission,
    IsOwnerOrReadOnly,
    IsOwnerOrStaff,
    TokenPermissionMixin,
    HasAPIPermission,
    get_user_role,
)

from .responses import (
    success_response,
    error_response,
    paginated_response,
    validation_error_response,
    permission_denied_response,
    not_found_response,
    unauthorized_response,
    server_error_response,
    rate_limit_response,
    created_response,
    updated_response,
    deleted_response,
    ResponseMixin,
)

__all__ = [
    # Views
    'CustomTokenObtainPairView',
    'RegisterView',
    'LogoutView',
    'ProfileView',
    'PasswordChangeView',
    'PasswordResetRequestView',
    'PasswordResetConfirmView',
    'TokenValidateView',
    'UserDeviceView',
    
    # Permissions
    'TokenBasedAuthentication',
    'RoleBasedPermission',
    'UserRolePermission',
    'StaffRolePermission',
    'AdminRolePermission',
    'IsOwnerOrReadOnly',
    'IsOwnerOrStaff',
    'TokenPermissionMixin',
    'HasAPIPermission',
    'get_user_role',
    
    # Responses
    'success_response',
    'error_response',
    'paginated_response',
    'validation_error_response',
    'permission_denied_response',
    'not_found_response',
    'unauthorized_response',
    'server_error_response',
    'rate_limit_response',
    'created_response',
    'updated_response',
    'deleted_response',
    'ResponseMixin',
]