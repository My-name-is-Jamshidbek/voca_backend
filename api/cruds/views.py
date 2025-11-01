"""
CRUD APIs - Token-based access for vocabulary and progress models
These APIs provide full CRUD operations with proper authentication
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema
from django.db import models
from apps.accounts.models import User
from apps.vocabulary.models import Word, Language, Book, Chapter, DifficultyLevel, Collection, CollectionWord
from apps.progress.models import UserProgress, UserSession
from .serializers import (
    WordSerializer, UserProgressSerializer, UserSessionSerializer,
    LanguageSerializer, BookSerializer, ChapterSerializer, DifficultyLevelSerializer,
    CollectionSerializer, CollectionWordSerializer
)
from ..base import success_response, error_response
import logging

logger = logging.getLogger(__name__)


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet with common functionality
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    def create(self, request, *args, **kwargs):
        """Override create to return standardized response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return success_response(
            data=serializer.data,
            message=f"{self.get_serializer().Meta.model.__name__} created successfully",
            status_code=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """Override update to return standardized response"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return success_response(
            data=serializer.data,
            message=f"{self.get_serializer().Meta.model.__name__} updated successfully"
        )
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to return standardized response"""
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return success_response(
            message=f"{self.get_serializer().Meta.model.__name__} deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
        )
    
    def list(self, request, *args, **kwargs):
        """Override list to return standardized response"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(
            data=serializer.data,
            message=f"{self.get_serializer().Meta.model.__name__} list retrieved successfully"
        )


class LanguageViewSet(BaseModelViewSet):
    """
    CRUD operations for Languages
    """
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    filterset_fields = ['is_active', 'code']
    search_fields = ['name', 'native_name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class BookViewSet(BaseModelViewSet):
    """
    CRUD operations for Books
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filterset_fields = ['language', 'publication_year']
    search_fields = ['title', 'author', 'isbn']
    ordering_fields = ['title', 'created_at']
    ordering = ['title']


class ChapterViewSet(BaseModelViewSet):
    """
    CRUD operations for Chapters
    """
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    filterset_fields = ['book']
    search_fields = ['title']
    ordering_fields = ['book', 'chapter_number']
    ordering = ['book', 'chapter_number']


class DifficultyLevelViewSet(BaseModelViewSet):
    """
    CRUD operations for Difficulty Levels
    """
    queryset = DifficultyLevel.objects.all()
    serializer_class = DifficultyLevelSerializer
    filterset_fields = ['level', 'cefr_level', 'numeric_level']
    search_fields = ['level', 'description']
    ordering_fields = ['numeric_level', 'level']
    ordering = ['numeric_level']


class WordViewSet(BaseModelViewSet):
    """
    CRUD operations for Words
    """
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    filterset_fields = ['language', 'book', 'chapter', 'difficulty_level', 'part_of_speech']
    search_fields = ['word', 'context_sentence']
    ordering_fields = ['word', 'created_at']
    ordering = ['word']
    
    @action(detail=True, methods=['post'])
    def mark_progress(self, request, pk=None):
        """Mark user progress for a word"""
        word = self.get_object()
        status_value = request.data.get('status', 'new')
        
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


class UserProgressViewSet(BaseModelViewSet):
    """
    CRUD operations for User Progress
    """
    serializer_class = UserProgressSerializer
    filterset_fields = ['status', 'word__language', 'word__difficulty_level']
    ordering = ['-last_reviewed']
    
    def get_queryset(self):
        # Users can only see their own progress
        return UserProgress.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_review(self, request, pk=None):
        """Update progress after a review"""
        progress = self.get_object()
        is_correct = request.data.get('is_correct', True)
        
        progress.update_progress(is_correct=is_correct)
        
        return success_response(
            data={'status': progress.status, 'next_review': progress.next_review},
            message="Progress updated successfully"
        )


class UserSessionViewSet(BaseModelViewSet):
    """
    CRUD operations for User Sessions
    """
    serializer_class = UserSessionSerializer
    filterset_fields = ['session_date']
    ordering = ['-session_date']
    
    def get_queryset(self):
        # Users can only see their own sessions
        return UserSession.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def log_activity(self, request):
        """Log learning activity to today's session"""
        words_learned = request.data.get('words_learned', 0)
        words_reviewed = request.data.get('words_reviewed', 0)
        time_minutes = request.data.get('time_minutes', 0)
        
        session, created = UserSession.get_or_create_today_session(request.user)
        session.add_learning_activity(
            words_learned=words_learned,
            words_reviewed=words_reviewed,
            time_minutes=time_minutes
        )
        
        return success_response(
            data={
                'session_date': session.session_date,
                'total_words_learned': session.words_learned,
                'total_words_reviewed': session.words_reviewed,
                'total_time_minutes': session.total_time_minutes,
            },
            message="Activity logged successfully"
        )


class CollectionViewSet(BaseModelViewSet):
    """
    CRUD operations for Collections
    """
    serializer_class = CollectionSerializer
    filterset_fields = ['is_public']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Users can see their own collections and public collections
        return Collection.objects.filter(
            models.Q(user=self.request.user) | models.Q(is_public=True)
        )
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_word(self, request, pk=None):
        """Add a word to the collection"""
        collection = self.get_object()
        word_id = request.data.get('word_id')
        
        try:
            word = Word.objects.get(id=word_id)
        except Word.DoesNotExist:
            return error_response(
                message="Word not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        collection_word, created = CollectionWord.objects.get_or_create(
            collection=collection,
            word=word
        )
        
        if created:
            return success_response(
                message="Word added to collection successfully"
            )
        else:
            return error_response(
                message="Word is already in this collection",
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['delete'])
    def remove_word(self, request, pk=None):
        """Remove a word from the collection"""
        collection = self.get_object()
        word_id = request.data.get('word_id')
        
        try:
            collection_word = CollectionWord.objects.get(
                collection=collection,
                word_id=word_id
            )
            collection_word.delete()
            return success_response(
                message="Word removed from collection successfully"
            )
        except CollectionWord.DoesNotExist:
            return error_response(
                message="Word not found in this collection",
                status_code=status.HTTP_404_NOT_FOUND
            )