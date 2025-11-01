"""
ViewSets for Vocabulary App Models
"""
from rest_framework import status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from apps.vocabulary.models import (
    Language, Book, Chapter, DifficultyLevel, Word, 
    WordTranslation, WordDefinition, Collection, CollectionWord
)
from ..common.base import BaseModelViewSet
from .serializers import (
    LanguageSerializer, BookSerializer, ChapterSerializer, DifficultyLevelSerializer,
    WordSerializer, WordTranslationSerializer, WordDefinitionSerializer,
    CollectionSerializer, CollectionWordSerializer
)
from ...base import success_response, error_response


class LanguageViewSet(BaseModelViewSet):
    """CRUD operations for Language model"""
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    filterset_fields = ['is_active']
    search_fields = ['name', 'native_name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active languages"""
        active_languages = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_languages, many=True)
        return success_response(
            data=serializer.data,
            message="Active languages retrieved successfully"
        )


class DifficultyLevelViewSet(BaseModelViewSet):
    """CRUD operations for DifficultyLevel model"""
    queryset = DifficultyLevel.objects.all()
    serializer_class = DifficultyLevelSerializer
    search_fields = ['level', 'cefr_level', 'description']
    filterset_fields = ['cefr_level']
    ordering_fields = ['numeric_level', 'level']
    ordering = ['numeric_level']


class BookViewSet(BaseModelViewSet):
    """CRUD operations for Book model"""
    queryset = Book.objects.select_related('language').all()
    serializer_class = BookSerializer
    search_fields = ['title', 'author', 'isbn', 'publisher']
    filterset_fields = ['language', 'publication_year']
    ordering_fields = ['title', 'author', 'publication_year', 'created_at']
    ordering = ['title']
    
    @action(detail=True, methods=['get'])
    def chapters(self, request, pk=None):
        """Get all chapters for this book"""
        book = self.get_object()
        chapters = Chapter.objects.filter(book=book).order_by('chapter_number')
        serializer = ChapterSerializer(chapters, many=True)
        return success_response(
            data=serializer.data,
            message="Book chapters retrieved successfully"
        )
    
    @action(detail=True, methods=['get'])
    def words(self, request, pk=None):
        """Get all words for this book"""
        book = self.get_object()
        words = Word.objects.filter(book=book).select_related('language', 'difficulty_level')
        serializer = WordSerializer(words, many=True)
        return success_response(
            data=serializer.data,
            message="Book words retrieved successfully"
        )


class ChapterViewSet(BaseModelViewSet):
    """CRUD operations for Chapter model"""
    queryset = Chapter.objects.select_related('book', 'book__language').all()
    serializer_class = ChapterSerializer
    search_fields = ['title', 'description']
    filterset_fields = ['book']
    ordering_fields = ['book', 'chapter_number', 'created_at']
    ordering = ['book', 'chapter_number']
    
    @action(detail=True, methods=['get'])
    def words(self, request, pk=None):
        """Get all words for this chapter"""
        chapter = self.get_object()
        words = Word.objects.filter(chapter=chapter).select_related('language', 'difficulty_level')
        serializer = WordSerializer(words, many=True)
        return success_response(
            data=serializer.data,
            message="Chapter words retrieved successfully"
        )


class WordViewSet(BaseModelViewSet):
    """CRUD operations for Word model"""
    queryset = Word.objects.select_related('language', 'book', 'chapter', 'difficulty_level').all()
    serializer_class = WordSerializer
    search_fields = ['word', 'pronunciation', 'context_sentence']
    filterset_fields = ['language', 'book', 'chapter', 'difficulty_level', 'part_of_speech']
    ordering_fields = ['word', 'difficulty_level', 'created_at']
    ordering = ['word']
    
    @action(detail=True, methods=['get'])
    def translations(self, request, pk=None):
        """Get all translations for this word"""
        word = self.get_object()
        translations = WordTranslation.objects.filter(word=word).select_related('language')
        serializer = WordTranslationSerializer(translations, many=True)
        return success_response(
            data=serializer.data,
            message="Word translations retrieved successfully"
        )
    
    @action(detail=True, methods=['get'])
    def definitions(self, request, pk=None):
        """Get all definitions for this word"""
        word = self.get_object()
        definitions = WordDefinition.objects.filter(word=word).select_related('language')
        serializer = WordDefinitionSerializer(definitions, many=True)
        return success_response(
            data=serializer.data,
            message="Word definitions retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def by_difficulty(self, request):
        """Get words grouped by difficulty level"""
        difficulty = request.query_params.get('difficulty')
        if difficulty:
            words = self.queryset.filter(difficulty_level__cefr_level=difficulty)
            serializer = self.get_serializer(words, many=True)
            return success_response(
                data=serializer.data,
                message=f"Words with {difficulty} difficulty retrieved successfully"
            )
        return error_response(
            message="difficulty parameter required", 
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def mark_progress(self, request, pk=None):
        """Mark user progress for a word"""
        word = self.get_object()
        status_value = request.data.get('status', 'new')
        
        from apps.progress.models import UserProgress
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            word=word,
            defaults={'status': status_value}
        )
        
        if not created:
            progress.status = status_value
            progress.save()
        
        return success_response(
            data={'status': progress.status},
            message="Word progress updated successfully"
        )


class WordTranslationViewSet(BaseModelViewSet):
    """CRUD operations for WordTranslation model"""
    queryset = WordTranslation.objects.select_related('word', 'language').all()
    serializer_class = WordTranslationSerializer
    search_fields = ['translation', 'word__word']
    filterset_fields = ['word', 'language']
    ordering_fields = ['word', 'language', 'created_at']
    ordering = ['word', 'language']


class WordDefinitionViewSet(BaseModelViewSet):
    """CRUD operations for WordDefinition model"""
    queryset = WordDefinition.objects.select_related('word', 'language').all()
    serializer_class = WordDefinitionSerializer
    search_fields = ['definition', 'example_sentence', 'word__word']
    filterset_fields = ['word', 'language']
    ordering_fields = ['word', 'language', 'created_at']
    ordering = ['word', 'language']


class CollectionViewSet(BaseModelViewSet):
    """CRUD operations for Collection model"""
    queryset = Collection.objects.select_related('user').prefetch_related('collection_words__word').all()
    serializer_class = CollectionSerializer
    search_fields = ['name', 'description']
    filterset_fields = ['is_public', 'user']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """Filter collections based on user permissions"""
        queryset = super().get_queryset()
        
        # Users can see their own collections + public collections
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            queryset = queryset.filter(
                Q(user=self.request.user) | Q(is_public=True)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_word(self, request, pk=None):
        """Add a word to this collection"""
        collection = self.get_object()
        word_id = request.data.get('word_id')
        
        if not word_id:
            return error_response(
                message="word_id required", 
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            word = Word.objects.get(id=word_id)
            collection_word, created = CollectionWord.objects.get_or_create(
                collection=collection, word=word
            )
            
            if created:
                return success_response(message='Word added to collection')
            else:
                return success_response(message='Word already in collection')
        
        except Word.DoesNotExist:
            return error_response(
                message='Word not found', 
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'])
    def remove_word(self, request, pk=None):
        """Remove a word from this collection"""
        collection = self.get_object()
        word_id = request.query_params.get('word_id')
        
        if not word_id:
            return error_response(
                message="word_id required", 
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            CollectionWord.objects.filter(
                collection=collection, word_id=word_id
            ).delete()
            return success_response(message='Word removed from collection')
        
        except CollectionWord.DoesNotExist:
            return error_response(
                message='Word not in collection', 
                status_code=status.HTTP_404_NOT_FOUND
            )


class CollectionWordViewSet(BaseModelViewSet):
    """CRUD operations for CollectionWord model"""
    queryset = CollectionWord.objects.select_related('collection', 'word').all()
    serializer_class = CollectionWordSerializer
    filterset_fields = ['collection', 'word']
    ordering_fields = ['added_at']
    ordering = ['-added_at']