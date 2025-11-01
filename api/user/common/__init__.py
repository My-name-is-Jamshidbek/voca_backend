"""
Common module for User APIs
Exports all shared utilities and base classes
"""

from .base import (
    IsAuthenticatedUser,
    IsOwner,
    IsUserRole,
    UserAuthenticationMixin,
    UserResponseMixin,
    UserAPIView,
    paginate_response,
    calculate_learning_stats,
    calculate_streak,
)

__all__ = [
    'IsAuthenticatedUser',
    'IsOwner',
    'IsUserRole',
    'UserAuthenticationMixin',
    'UserResponseMixin',
    'UserAPIView',
    'paginate_response',
    'calculate_learning_stats',
    'calculate_streak',
]
