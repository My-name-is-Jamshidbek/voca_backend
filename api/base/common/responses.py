"""
Common response utilities for API base modules
Standardized response format for consistent API responses
"""

from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


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


def validation_error_response(errors, message="Validation failed"):
    """
    Return a standardized validation error response
    """
    return error_response(message, errors, status.HTTP_400_BAD_REQUEST)


def permission_denied_response(message="Permission denied"):
    """
    Return a standardized permission denied response
    """
    return error_response(message, status_code=status.HTTP_403_FORBIDDEN)


def not_found_response(message="Resource not found"):
    """
    Return a standardized not found response
    """
    return error_response(message, status_code=status.HTTP_404_NOT_FOUND)


def unauthorized_response(message="Authentication required"):
    """
    Return a standardized unauthorized response
    """
    return error_response(message, status_code=status.HTTP_401_UNAUTHORIZED)


class ResponseMixin:
    """
    Mixin to add standardized response methods to views
    """
    
    def success_response(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        return success_response(data, message, status_code)
    
    def error_response(self, message="Error", details=None, status_code=status.HTTP_400_BAD_REQUEST):
        return error_response(message, details, status_code)
    
    def validation_error_response(self, errors, message="Validation failed"):
        return validation_error_response(errors, message)
    
    def permission_denied_response(self, message="Permission denied"):
        return permission_denied_response(message)
    
    def not_found_response(self, message="Resource not found"):
        return not_found_response(message)
    
    def unauthorized_response(self, message="Authentication required"):
        return unauthorized_response(message)