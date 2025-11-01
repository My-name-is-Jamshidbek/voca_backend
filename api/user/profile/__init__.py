"""
Profile module for User APIs
"""

from .views import UserProfileViewSet
from .serializers import (
    UserDetailSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    ChangePasswordSerializer,
    UserStatisticsSerializer,
    UserDeviceSerializer
)

__all__ = [
    'UserProfileViewSet',
    'UserDetailSerializer',
    'UserProfileSerializer',
    'UserProfileUpdateSerializer',
    'ChangePasswordSerializer',
    'UserStatisticsSerializer',
    'UserDeviceSerializer',
]
