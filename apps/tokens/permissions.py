from rest_framework import permissions


class IsTokenAdmin(permissions.BasePermission):
    """
    Custom permission to only allow token administrators to access API client tokens.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff or request.user.is_superuser)
        )


class CanManageTokens(permissions.BasePermission):
    """
    Custom permission to allow token management.
    Staff users can manage mobile tokens, superusers can manage all tokens.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_staff
        )
    
    def has_object_permission(self, request, view, obj):
        # Superusers can manage all tokens
        if request.user.is_superuser:
            return True
        
        # Staff users can only manage tokens they created
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False


class IsTokenOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow only token owners or admins to access token details.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Superusers and staff can access all tokens
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # Regular users can only access their own tokens
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False


class ReadOnlyOrTokenAdmin(permissions.BasePermission):
    """
    Custom permission to allow read-only access for authenticated users,
    but write access only for token administrators.
    """
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for staff/superuser
        return request.user.is_staff or request.user.is_superuser