"""
Custom permissions for role-based access control and token authentication
"""

from rest_framework.permissions import BasePermission
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext_lazy as _
import logging

from apps.accounts.models import User
from apps.tokens.models import MobileAppToken, APIClientToken, TokenUsageLog

logger = logging.getLogger(__name__)


class TokenBasedAuthentication(BaseAuthentication):
    """
    Custom authentication backend that supports both mobile app tokens and API client tokens
    """
    keyword = 'Bearer'
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth = self.get_authorization_header(request).split()
        
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None
        
        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise AuthenticationFailed(msg)
        
        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise AuthenticationFailed(msg)
        
        return self.authenticate_credentials(token, request)
    
    def authenticate_credentials(self, token, request):
        """
        Authenticate the token and return the user and token instance.
        """
        # Determine token type based on prefix
        if token.startswith('mob_'):
            return self.authenticate_mobile_token(token, request)
        elif token.startswith('api_'):
            return self.authenticate_api_token(token, request)
        else:
            # Fall back to JWT authentication for other tokens
            return None
    
    def authenticate_mobile_token(self, token, request):
        """Authenticate mobile app token"""
        try:
            mobile_token = MobileAppToken.objects.select_related('app_version', 'created_by').get(
                token=token,
                status='active'
            )
        except MobileAppToken.DoesNotExist:
            raise AuthenticationFailed(_('Invalid mobile token.'))
        
        if not mobile_token.is_valid():
            raise AuthenticationFailed(_('Mobile token has expired or exceeded usage limit.'))
        
        # Check IP restrictions
        if mobile_token.allowed_ips:
            client_ip = self.get_client_ip(request)
            if client_ip not in mobile_token.allowed_ips:
                raise AuthenticationFailed(_('Access denied from this IP address.'))
        
        # Log token usage
        self.log_token_usage(mobile_token, request, 'mobile')
        
        # Increment usage count
        mobile_token.increment_usage()
        
        # Create a pseudo-user with the token's role
        user = mobile_token.created_by
        user.token_role = mobile_token.role
        user.mobile_token = mobile_token
        
        return (user, mobile_token)
    
    def authenticate_api_token(self, token, request):
        """Authenticate API client token"""
        try:
            api_token = APIClientToken.objects.select_related('created_by').get(
                token=token,
                status='active'
            )
        except APIClientToken.DoesNotExist:
            raise AuthenticationFailed(_('Invalid API token.'))
        
        if not api_token.is_valid():
            raise AuthenticationFailed(_('API token has expired or exceeded usage limit.'))
        
        # Check IP restrictions
        if api_token.allowed_ips:
            client_ip = self.get_client_ip(request)
            if client_ip not in api_token.allowed_ips:
                raise AuthenticationFailed(_('Access denied from this IP address.'))
        
        # Check endpoint restrictions
        if api_token.allowed_endpoints:
            request_path = request.path_info
            if not any(endpoint in request_path for endpoint in api_token.allowed_endpoints):
                raise AuthenticationFailed(_('Access denied to this endpoint.'))
        
        # Log token usage
        self.log_token_usage(api_token, request, 'api')
        
        # Increment usage count
        api_token.increment_usage()
        
        # Create a pseudo-user with the token's permissions
        user = api_token.created_by
        user.api_token = api_token
        
        return (user, api_token)
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def log_token_usage(self, token, request, token_type):
        """Log token usage for monitoring"""
        try:
            TokenUsageLog.objects.create(
                token_type=token_type,
                token_id=str(token.id),
                token_name=token.name,
                endpoint=request.path_info,
                method=request.method,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                status_code=200,  # Will be updated by middleware
            )
        except Exception as e:
            logger.error(f"Failed to log token usage: {e}")


class RoleBasedPermission(BasePermission):
    """
    Base permission class for role-based access control
    """
    required_role = None
    required_roles = []  # Alternative: list of allowed roles
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has mobile token role
        if hasattr(request.user, 'token_role'):
            user_role = request.user.token_role
        else:
            # For JWT authenticated users, determine role based on user properties
            if request.user.is_superuser:
                user_role = 'admin'
            elif request.user.is_staff:
                user_role = 'staff'
            else:
                user_role = 'user'
        
        # Check single required role
        if self.required_role:
            return user_role == self.required_role
        
        # Check multiple allowed roles
        if self.required_roles:
            return user_role in self.required_roles
        
        # If no role specified, allow any authenticated user
        return True


class UserRolePermission(RoleBasedPermission):
    """Permission for user role - allows users, staff, and admin"""
    required_roles = ['user', 'staff', 'admin']


class StaffRolePermission(RoleBasedPermission):
    """Permission for staff role - allows staff and admin only"""
    required_roles = ['staff', 'admin']


class AdminRolePermission(RoleBasedPermission):
    """Permission for admin role - allows admin only"""
    required_role = 'admin'


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Read permissions are allowed to any request.
    Write permissions are only allowed to the owner of the object.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user if hasattr(obj, 'user') else obj == request.user


class IsOwnerOrStaff(BasePermission):
    """
    Custom permission that allows owners or staff to access objects
    """
    
    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if request.user.is_staff:
            return True
        
        # Owners can access their own objects
        return obj.user == request.user if hasattr(obj, 'user') else obj == request.user


class TokenPermissionMixin:
    """
    Mixin to check API client token permissions for specific models and actions
    """
    
    def check_token_permission(self, request, action, model_name=None):
        """
        Check if the current token has permission for the specified action
        """
        # Skip permission check for JWT authenticated users (not token-based)
        if not hasattr(request.user, 'api_token'):
            return True
        
        api_token = request.user.api_token
        
        # If no model specified, use the view's model
        if not model_name:
            if hasattr(self, 'model') and self.model:
                model_name = self.model.__name__
            elif hasattr(self, 'queryset') and self.queryset is not None:
                model_name = self.queryset.model.__name__
            else:
                return False
        
        # Get token permissions for this model
        try:
            permission = api_token.model_permissions.get(model_name=model_name)
        except:
            # If no permission found, deny access
            return False
        
        # Check specific action permission
        action_permissions = {
            'create': permission.can_create,
            'list': permission.can_list,
            'retrieve': permission.can_read,
            'update': permission.can_update,
            'partial_update': permission.can_update,
            'destroy': permission.can_delete,
            'bulk_create': permission.can_bulk_create,
            'bulk_update': permission.can_bulk_update,
            'bulk_delete': permission.can_bulk_delete,
        }
        
        return action_permissions.get(action, False)
    
    def filter_restricted_fields(self, data, request, action='update'):
        """
        Filter out restricted fields from request data based on token permissions
        """
        if not hasattr(request.user, 'api_token'):
            return data
        
        api_token = request.user.api_token
        model_name = self.get_model_name()
        
        try:
            permission = api_token.model_permissions.get(model_name=model_name)
            restricted_fields = permission.restricted_fields
            readonly_fields = permission.readonly_fields
            
            # Remove restricted fields
            if restricted_fields:
                for field in restricted_fields:
                    data.pop(field, None)
            
            # Remove readonly fields during updates
            if action in ['update', 'partial_update'] and readonly_fields:
                for field in readonly_fields:
                    data.pop(field, None)
        except:
            pass
        
        return data
    
    def get_model_name(self):
        """Get model name for permission checking"""
        if hasattr(self, 'model') and self.model:
            return self.model.__name__
        elif hasattr(self, 'queryset') and self.queryset is not None:
            return self.queryset.model.__name__
        return None


class HasAPIPermission(BasePermission):
    """
    Permission class to check API client token permissions
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Allow JWT authenticated users
        if not hasattr(request.user, 'api_token'):
            return True
        
        # Check token permissions for token-based authentication
        if hasattr(view, 'check_token_permission'):
            action = getattr(view, 'action', request.method.lower())
            return view.check_token_permission(request, action)
        
        return False


# Utility function to get user role
def get_user_role(user):
    """Get user role for permission checking"""
    if hasattr(user, 'token_role'):
        return user.token_role
    elif user.is_superuser:
        return 'admin'
    elif user.is_staff:
        return 'staff'
    else:
        return 'user'