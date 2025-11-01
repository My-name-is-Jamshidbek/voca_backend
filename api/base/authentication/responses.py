"""
Standardized response utilities for consistent API responses
"""

from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def success_response(data=None, message="Success", status_code=status.HTTP_200_OK, extra_data=None):
    """
    Return a standardized success response
    
    Args:
        data: The main response data
        message: Success message
        status_code: HTTP status code
        extra_data: Additional data to include in response
    
    Returns:
        Response: DRF Response object with standardized format
    """
    response_data = {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': timezone.now().isoformat()
    }
    
    # Add extra data if provided
    if extra_data:
        response_data.update(extra_data)
    
    return Response(response_data, status=status_code)


def error_response(message="Error", details=None, status_code=status.HTTP_400_BAD_REQUEST, error_code=None):
    """
    Return a standardized error response
    
    Args:
        message: Error message
        details: Additional error details
        status_code: HTTP status code
        error_code: Custom error code for client handling
    
    Returns:
        Response: DRF Response object with standardized error format
    """
    response_data = {
        'success': False,
        'error': True,
        'message': message,
        'timestamp': timezone.now().isoformat()
    }
    
    if details is not None:
        response_data['details'] = details
    
    if error_code is not None:
        response_data['error_code'] = error_code
    
    # Log error for debugging
    logger.error(f"API Error: {message} | Details: {details} | Status: {status_code}")
    
    return Response(response_data, status=status_code)


def paginated_response(data, paginator, message="Data retrieved successfully"):
    """
    Return a standardized paginated response
    
    Args:
        data: The paginated data
        paginator: Django paginator object
        message: Success message
    
    Returns:
        Response: DRF Response object with pagination metadata
    """
    response_data = {
        'success': True,
        'message': message,
        'data': data,
        'pagination': {
            'count': paginator.page.paginator.count,
            'num_pages': paginator.page.paginator.num_pages,
            'current_page': paginator.page.number,
            'page_size': paginator.page_size,
            'has_next': paginator.page.has_next(),
            'has_previous': paginator.page.has_previous(),
            'next_page': paginator.page.next_page_number() if paginator.page.has_next() else None,
            'previous_page': paginator.page.previous_page_number() if paginator.page.has_previous() else None,
        },
        'timestamp': timezone.now().isoformat()
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


def validation_error_response(errors, message="Validation failed"):
    """
    Return a standardized validation error response
    
    Args:
        errors: Validation errors (usually from serializer.errors)
        message: Error message
    
    Returns:
        Response: DRF Response object with validation errors
    """
    # Flatten nested validation errors
    flattened_errors = {}
    
    if isinstance(errors, dict):
        for field, error_list in errors.items():
            if isinstance(error_list, list):
                flattened_errors[field] = error_list
            else:
                flattened_errors[field] = [str(error_list)]
    else:
        flattened_errors['non_field_errors'] = [str(errors)]
    
    return error_response(
        message=message,
        details=flattened_errors,
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code="VALIDATION_ERROR"
    )


def permission_denied_response(message="Permission denied"):
    """
    Return a standardized permission denied response
    """
    return error_response(
        message=message,
        status_code=status.HTTP_403_FORBIDDEN,
        error_code="PERMISSION_DENIED"
    )


def not_found_response(message="Resource not found"):
    """
    Return a standardized not found response
    """
    return error_response(
        message=message,
        status_code=status.HTTP_404_NOT_FOUND,
        error_code="NOT_FOUND"
    )


def unauthorized_response(message="Authentication required"):
    """
    Return a standardized unauthorized response
    """
    return error_response(
        message=message,
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_code="UNAUTHORIZED"
    )


def server_error_response(message="Internal server error", error_details=None):
    """
    Return a standardized server error response
    """
    return error_response(
        message=message,
        details=error_details,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_ERROR"
    )


def rate_limit_response(message="Rate limit exceeded", retry_after=None):
    """
    Return a standardized rate limit response
    """
    extra_data = {}
    if retry_after:
        extra_data['retry_after'] = retry_after
    
    response = error_response(
        message=message,
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        error_code="RATE_LIMIT_EXCEEDED"
    )
    
    if retry_after:
        response['Retry-After'] = str(retry_after)
    
    return response


def created_response(data=None, message="Resource created successfully"):
    """
    Return a standardized creation success response
    """
    return success_response(
        data=data,
        message=message,
        status_code=status.HTTP_201_CREATED
    )


def updated_response(data=None, message="Resource updated successfully"):
    """
    Return a standardized update success response
    """
    return success_response(
        data=data,
        message=message,
        status_code=status.HTTP_200_OK
    )


def deleted_response(message="Resource deleted successfully"):
    """
    Return a standardized deletion success response
    """
    return success_response(
        data=None,
        message=message,
        status_code=status.HTTP_204_NO_CONTENT
    )


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
    
    def created_response(self, data=None, message="Resource created successfully"):
        return created_response(data, message)
    
    def updated_response(self, data=None, message="Resource updated successfully"):
        return updated_response(data, message)
    
    def deleted_response(self, message="Resource deleted successfully"):
        return deleted_response(message)