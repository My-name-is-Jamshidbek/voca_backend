"""
User API URL Configuration
Routes for profile, learning, and analytics endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.user.profile import UserProfileViewSet
from api.user.learning import WordsViewSet, CollectionsViewSet
from api.user.analytics import AnalyticsViewSet

# Create router for ViewSets
router = DefaultRouter()
router.register(r'profile', UserProfileViewSet, basename='user-profile')
router.register(r'learning/words', WordsViewSet, basename='user-words')
router.register(r'learning/collections', CollectionsViewSet, basename='user-collections')
router.register(r'analytics', AnalyticsViewSet, basename='user-analytics')

app_name = 'user'

urlpatterns = [
    path('', include(router.urls)),
]
