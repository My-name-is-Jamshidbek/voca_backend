"""
Common base classes and utilities for User APIs
Shared components for authentication, permissions, and responses
"""

from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class IsAuthenticatedUser(BasePermission):
    """
    Permission to check if user is authenticated
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsOwner(BasePermission):
    """
    Permission to check if user is the owner of the object
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or obj.user_id == request.user.id


class IsUserRole(BasePermission):
    """
    Permission to check if user has user role
    """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and (request.user.role == 'user' or not hasattr(request.user, 'role'))
        )


class UserAuthenticationMixin:
    """
    Mixin for user API views with JWT authentication
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedUser]
    
    def get_user(self):
        """Get current authenticated user"""
        return self.request.user
    
    def get_user_id(self):
        """Get current user ID"""
        return self.request.user.id


class UserResponseMixin:
    """
    Mixin to add standardized response methods for user APIs
    """
    
    def success_response(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        """Return a standardized success response"""
        response_data = {
            'success': True,
            'message': message,
            'data': data,
            'timestamp': timezone.now().isoformat()
        }
        return Response(response_data, status=status_code)
    
    def error_response(self, message="Error", details=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Return a standardized error response"""
        response_data = {
            'success': False,
            'error': True,
            'message': message,
            'details': details,
            'timestamp': timezone.now().isoformat()
        }
        return Response(response_data, status=status_code)
    
    def validation_error_response(self, errors, message="Validation failed"):
        """Return a standardized validation error response"""
        return self.error_response(message, errors, status.HTTP_400_BAD_REQUEST)
    
    def permission_denied_response(self, message="Permission denied"):
        """Return a permission denied response"""
        return self.error_response(message, status_code=status.HTTP_403_FORBIDDEN)
    
    def not_found_response(self, message="Resource not found"):
        """Return a not found response"""
        return self.error_response(message, status_code=status.HTTP_404_NOT_FOUND)
    
    def unauthorized_response(self, message="Authentication required"):
        """Return an unauthorized response"""
        return self.error_response(message, status_code=status.HTTP_401_UNAUTHORIZED)


class UserAPIView(APIView, UserAuthenticationMixin, UserResponseMixin):
    """
    Base API View for User APIs with authentication and response handling
    """
    pass


def paginate_response(data, page, page_size, total_count):
    """
    Add pagination information to response
    
    Args:
        data: Response data
        page: Current page number
        page_size: Items per page
        total_count: Total number of items
    
    Returns:
        Dictionary with pagination info
    """
    total_pages = (total_count + page_size - 1) // page_size
    
    return {
        'data': data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total_count': total_count,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1,
        }
    }


def calculate_learning_stats(user):
    """
    Calculate user's learning statistics
    
    Args:
        user: User instance
    
    Returns:
        Dictionary with learning statistics
    """
    from apps.progress.models import UserProgress
    from apps.vocabulary.models import Word
    
    try:
        total_words = Word.objects.count()
        user_progress = UserProgress.objects.filter(user=user)
        words_learned = user_progress.filter(mastery_level__gte=3).count()
        words_in_progress = user_progress.filter(mastery_level__in=[1, 2]).count()
        review_due = user_progress.filter(
            next_review_date__lte=timezone.now()
        ).count()
        
        return {
            'total_words_available': total_words,
            'words_learned': words_learned,
            'words_in_progress': words_in_progress,
            'words_not_started': total_words - words_learned - words_in_progress,
            'review_due': review_due,
            'learning_percentage': (
                (words_learned / total_words * 100) if total_words > 0 else 0
            ),
        }
    except Exception as e:
        logger.error(f"Error calculating learning stats: {e}")
        return {
            'total_words_available': 0,
            'words_learned': 0,
            'words_in_progress': 0,
            'words_not_started': 0,
            'review_due': 0,
            'learning_percentage': 0,
        }


def calculate_streak(user):
    """
    Calculate user's learning streak
    
    Args:
        user: User instance
    
    Returns:
        Dictionary with streak information
    """
    from apps.progress.models import UserSession
    from datetime import timedelta
    
    try:
        today = timezone.now().date()
        current_streak = 0
        last_session_date = None
        
        sessions = UserSession.objects.filter(user=user).order_by('-session_date').values_list('session_date', flat=True).distinct()
        
        if sessions:
            for session_date in sessions:
                if current_streak == 0:
                    if session_date == today or session_date == today - timedelta(days=1):
                        current_streak = 1
                        last_session_date = session_date
                    else:
                        break
                else:
                    expected_date = last_session_date - timedelta(days=1)
                    if session_date == expected_date:
                        current_streak += 1
                        last_session_date = session_date
                    else:
                        break
        
        return {
            'current_streak': current_streak,
            'last_session_date': last_session_date,
            'max_streak': UserSession.objects.filter(user=user).values('user').annotate(
                streak_count=lambda: 1
            ).count() if hasattr(UserSession, 'streak_count') else 0,
        }
    except Exception as e:
        logger.error(f"Error calculating streak: {e}")
        return {
            'current_streak': 0,
            'last_session_date': None,
            'max_streak': 0,
        }
