"""
Base API utilities and permissions
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


class HealthCheckView(APIView):
    """
    Health Check endpoint - checks the status of the application
    """
    permission_classes = []
    
    def get(self, request):
        """Perform health check"""
        from django.db import connection
        from django.conf import settings
        
        health_status = {
            "status": "healthy",
            "database": "connected",
            "debug": settings.DEBUG,
            "timestamp": timezone.now().isoformat()
        }
        
        try:
            connection.ensure_connection()
            health_status["database"] = "connected"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            health_status["database"] = "disconnected"
            health_status["status"] = "unhealthy"
            return error_response(
                message="Service unhealthy",
                details=health_status,
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        return success_response(data=health_status, message="Service is healthy")


class APIRootView(APIView):
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
            "admin_apis": f"{base_url}/admin/",
            "staff_apis": f"{base_url}/staff/",
            "user_apis": f"{base_url}/user/",
            "public_apis": f"{base_url}/base/",
            "crud_apis": f"{base_url}/cruds/",
            "auth": f"{base_url}/base/auth/",
        }
        
        api_info = {
            "message": "Welcome to Voca API",
            "version": "1.0.0",
            "endpoints": endpoints,
            "authentication": "JWT Bearer Token required for protected endpoints",
            "roles": ["user", "staff", "admin"]
        }
        
        return success_response(data=api_info, message="API Root")