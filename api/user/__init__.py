"""
User API Module
Comprehensive user APIs for Flutter app with Bearer authentication
"""

from api.user.profile import UserProfileViewSet, UserDetailSerializer
from api.user.learning import WordsViewSet, CollectionsViewSet
from api.user.analytics import AnalyticsViewSet

__all__ = [
    'UserProfileViewSet',
    'WordsViewSet',
    'CollectionsViewSet',
    'AnalyticsViewSet',
    'UserDetailSerializer',
]
