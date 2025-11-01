"""
URL patterns for Progress App CRUD APIs
"""
from rest_framework.routers import DefaultRouter
from .views import UserProgressViewSet, UserSessionViewSet

# Create router for progress app
progress_router = DefaultRouter()
progress_router.register(r'user-progress', UserProgressViewSet, basename='user-progress')
progress_router.register(r'user-sessions', UserSessionViewSet, basename='user-session')

# Export patterns
urlpatterns = progress_router.urls