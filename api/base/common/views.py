"""
Common base utilities for API base modules
Shared components, permissions, responses, and base classes
"""

from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.utils import timezone
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


class BaseAPIView(APIView):
    """
    Base API View with common functionality and role-based permissions
    """
    
    def handle_exception(self, exc):
        """
        Handle exceptions and return consistent error responses
        """
        logger.error(f"API Exception: {exc}")
        
        response = super().handle_exception(exc)
        
        # Customize error response format
        if hasattr(response, 'data'):
            custom_response_data = {
                'success': False,
                'error': True,
                'message': 'An error occurred',
                'details': response.data,
                'timestamp': timezone.now().isoformat()
            }
            response.data = custom_response_data
        
        return response


def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """
    Return a standardized success response
    """
    response_data = {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': timezone.now().isoformat()
    }
    return Response(response_data, status=status_code)


def error_response(message="Error", details=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Return a standardized error response
    """
    response_data = {
        'success': False,
        'error': True,
        'message': message,
        'details': details,
        'timestamp': timezone.now().isoformat()
    }
    return Response(response_data, status=status_code)


class ResponseMixin:
    """
    Mixin to add standardized response methods to views
    """
    
    def success_response(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        return success_response(data, message, status_code)
    
    def error_response(self, message="Error", details=None, status_code=status.HTTP_400_BAD_REQUEST):
        return error_response(message, details, status_code)
    
    def validation_error_response(self, errors, message="Validation failed"):
        return error_response(message, errors, status.HTTP_400_BAD_REQUEST)
    
    def permission_denied_response(self, message="Permission denied"):
        return error_response(message, status_code=status.HTTP_403_FORBIDDEN)
    
    def not_found_response(self, message="Resource not found"):
        return error_response(message, status_code=status.HTTP_404_NOT_FOUND)
    
    def unauthorized_response(self, message="Authentication required"):
        return error_response(message, status_code=status.HTTP_401_UNAUTHORIZED)


class APIRootView(APIView, ResponseMixin):
    """
    API Root endpoint - provides an overview of available endpoints
    """
    permission_classes = []
    
    def get(self, request):
        """Return API information"""
        base_url = request.build_absolute_uri().rstrip('/')
        
        endpoints = {
            "health": f"{base_url}/health/",
            "docs": f"{base_url}/docs/",
            "admin_apis": f"{base_url}/../admin/",
            "staff_apis": f"{base_url}/../staff/",
            "user_apis": f"{base_url}/../user/",
            "crud_apis": f"{base_url}/../cruds/",
            "auth": f"{base_url}/auth/",
        }
        
        api_info = {
            "message": "Welcome to Voca Base API",
            "version": "1.0.0",
            "endpoints": endpoints,
            "authentication": "JWT Bearer Token required for protected endpoints",
            "roles": ["user", "staff", "admin"]
        }
        
        return self.success_response(data=api_info, message="API Root")