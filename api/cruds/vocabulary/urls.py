"""
URL patterns for Vocabulary App CRUD APIs
"""
from rest_framework.routers import DefaultRouter
from .views import (
    LanguageViewSet, DifficultyLevelViewSet, BookViewSet, ChapterViewSet,
    WordViewSet, WordTranslationViewSet, WordDefinitionViewSet,
    CollectionViewSet, CollectionWordViewSet
)

# Create router for vocabulary app
vocabulary_router = DefaultRouter()
vocabulary_router.register(r'languages', LanguageViewSet, basename='language')
vocabulary_router.register(r'difficulty-levels', DifficultyLevelViewSet, basename='difficulty-level')
vocabulary_router.register(r'books', BookViewSet, basename='book')
vocabulary_router.register(r'chapters', ChapterViewSet, basename='chapter')
vocabulary_router.register(r'words', WordViewSet, basename='word')
vocabulary_router.register(r'word-translations', WordTranslationViewSet, basename='word-translation')
vocabulary_router.register(r'word-definitions', WordDefinitionViewSet, basename='word-definition')
vocabulary_router.register(r'collections', CollectionViewSet, basename='collection')
vocabulary_router.register(r'collection-words', CollectionWordViewSet, basename='collection-word')

# Export patterns
urlpatterns = vocabulary_router.urls