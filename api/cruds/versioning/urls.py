"""
URL patterns for Versioning App CRUD APIs
"""
from rest_framework.routers import DefaultRouter
from .views import AppVersionViewSet

# Create router for versioning app
versioning_router = DefaultRouter()
versioning_router.register(r'app-versions', AppVersionViewSet, basename='app-version')

# Export patterns
urlpatterns = versioning_router.urls