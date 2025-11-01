"""
CRUD API URLs for Vocabulary and Progress Models
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LanguageViewSet,
    BookViewSet,
    ChapterViewSet,
    DifficultyLevelViewSet,
    WordViewSet,
    UserProgressViewSet,
    UserSessionViewSet,
    CollectionViewSet,
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'languages', LanguageViewSet, basename='language')
router.register(r'books', BookViewSet, basename='book')
router.register(r'chapters', ChapterViewSet, basename='chapter')
router.register(r'difficulty-levels', DifficultyLevelViewSet, basename='difficulty-level')
router.register(r'words', WordViewSet, basename='word')
router.register(r'user-progress', UserProgressViewSet, basename='user-progress')
router.register(r'user-sessions', UserSessionViewSet, basename='user-session')
router.register(r'collections', CollectionViewSet, basename='collection')

app_name = 'cruds'

urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
]