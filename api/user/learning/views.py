"""
Learning Views
Vocabulary learning and progress tracking APIs for Flutter app
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from django.db.models import Q
from apps.vocabulary.models import Word, Collection, CollectionWord, DifficultyLevel
from apps.progress.models import UserProgress, UserSession
from ..common import UserResponseMixin, paginate_response
from .serializers import (
    WordDetailSerializer, WordListSerializer, UserProgressSerializer,
    UserProgressUpdateSerializer, CollectionSerializer, CollectionCreateSerializer,
    UserSessionSerializer, CollectionWordSerializer
)
import logging

logger = logging.getLogger(__name__)


class WordsViewSet(viewsets.ViewSet, UserResponseMixin):
    """
    Words Learning ViewSet
    
    Comprehensive API endpoints for vocabulary learning
    Requires Bearer token authentication
    
    Endpoints:
        GET    /api/user/learning/words/                      - List words (paginated, filterable)
        GET    /api/user/learning/words/{id}/                 - Get word details
        GET    /api/user/learning/words/by_difficulty/        - Filter by difficulty
        GET    /api/user/learning/words/due_for_review/       - Get words due for review
        GET    /api/user/learning/words/random/               - Get random words
        POST   /api/user/learning/words/{id}/mark_progress/   - Mark word progress
    """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        List all words with pagination and filtering
        
        Query Parameters:
            - page: Page number (default: 1)
            - page_size: Items per page (default: 20, max: 100)
            - difficulty: Filter by difficulty level (e.g., A1, A2, B1)
            - search: Search by word name
            - collection_id: Filter by collection
        
        Returns:
            {
                "success": true,
                "message": "Words retrieved successfully",
                "data": {
                    "data": [...],
                    "pagination": {
                        "page": 1,
                        "page_size": 20,
                        "total_count": 5000,
                        "total_pages": 250,
                        "has_next": true,
                        "has_previous": false
                    }
                }
            }
        """
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        search = request.query_params.get('search', '')
        difficulty = request.query_params.get('difficulty', '')
        
        queryset = Word.objects.all()
        
        if search:
            queryset = queryset.filter(Q(word__icontains=search))
        
        if difficulty:
            queryset = queryset.filter(difficulty_level__cefr_level=difficulty)
        
        total_count = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        
        words = queryset[start:end]
        serializer = WordListSerializer(words, many=True)
        
        pagination_data = paginate_response(
            data=serializer.data,
            page=page,
            page_size=page_size,
            total_count=total_count
        )
        
        return self.success_response(
            data=pagination_data,
            message="Words retrieved successfully"
        )
    
    def retrieve(self, request, pk=None):
        """
        Get word details with translations and definitions
        
        Returns:
            {
                "success": true,
                "message": "Word retrieved successfully",
                "data": {
                    "id": "word-1",
                    "word": "Hello",
                    "phonetic": "həˈloʊ",
                    "difficulty_level": {...},
                    "translations": [...],
                    "definitions": [...]
                }
            }
        """
        try:
            word = Word.objects.get(id=pk)
            serializer = WordDetailSerializer(word)
            return self.success_response(
                data=serializer.data,
                message="Word retrieved successfully"
            )
        except Word.DoesNotExist:
            return self.not_found_response(message="Word not found")
    
    @action(detail=False, methods=['get'], url_path='by_difficulty')
    def by_difficulty(self, request):
        """
        Filter words by difficulty level
        
        Query Parameters:
            - level: CEFR level (A1, A2, B1, B2, C1, C2)
            - page: Page number (default: 1)
            - page_size: Items per page (default: 20)
        
        Returns:
            {
                "success": true,
                "message": "Words retrieved successfully",
                "data": {
                    "data": [...],
                    "pagination": {...}
                }
            }
        """
        level = request.query_params.get('level')
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        
        if not level:
            return self.error_response(
                message="Difficulty level is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = Word.objects.filter(difficulty_level__cefr_level=level)
        total_count = queryset.count()
        
        start = (page - 1) * page_size
        end = start + page_size
        
        words = queryset[start:end]
        serializer = WordListSerializer(words, many=True)
        
        pagination_data = paginate_response(
            data=serializer.data,
            page=page,
            page_size=page_size,
            total_count=total_count
        )
        
        return self.success_response(
            data=pagination_data,
            message="Words retrieved successfully"
        )
    
    @action(detail=False, methods=['get'], url_path='due_for_review')
    def due_for_review(self, request):
        """
        Get words due for review today
        
        Query Parameters:
            - page: Page number (default: 1)
            - page_size: Items per page (default: 20)
        
        Returns:
            {
                "success": true,
                "message": "Words due for review retrieved successfully",
                "data": {
                    "data": [...],
                    "pagination": {...}
                }
            }
        """
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        
        today = timezone.now()
        user_progress = UserProgress.objects.filter(
            user=request.user,
            next_review_date__lte=today
        ).select_related('word')
        
        total_count = user_progress.count()
        start = (page - 1) * page_size
        end = start + page_size
        
        progress_items = user_progress[start:end]
        serializer = UserProgressSerializer(progress_items, many=True)
        
        pagination_data = paginate_response(
            data=serializer.data,
            page=page,
            page_size=page_size,
            total_count=total_count
        )
        
        return self.success_response(
            data=pagination_data,
            message="Words due for review retrieved successfully"
        )
    
    @action(detail=False, methods=['get'], url_path='random')
    def random_words(self, request):
        """
        Get random words for learning
        
        Query Parameters:
            - count: Number of random words (default: 5, max: 20)
            - difficulty: Optional difficulty filter
        
        Returns:
            {
                "success": true,
                "message": "Random words retrieved successfully",
                "data": [...]
            }
        """
        count = min(int(request.query_params.get('count', 5)), 20)
        difficulty = request.query_params.get('difficulty')
        
        queryset = Word.objects.all()
        
        if difficulty:
            queryset = queryset.filter(difficulty_level__cefr_level=difficulty)
        
        words = queryset.order_by('?')[:count]
        serializer = WordListSerializer(words, many=True)
        
        return self.success_response(
            data=serializer.data,
            message="Random words retrieved successfully"
        )
    
    @action(detail=True, methods=['post'], url_path='mark_progress')
    def mark_progress(self, request, pk=None):
        """
        Mark word progress (record a review)
        
        Request Body:
            {
                "is_correct": true,
                "review_notes": "Easy to remember"
            }
        
        Returns:
            {
                "success": true,
                "message": "Progress updated successfully",
                "data": {
                    "mastery_level": 2,
                    "next_review_date": "2024-11-02T10:30:00Z",
                    "accuracy_percentage": 80.0
                }
            }
        """
        try:
            word = Word.objects.get(id=pk)
            
            progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                word=word,
                defaults={
                    'mastery_level': 0,
                    'times_reviewed': 0,
                    'correct_answers': 0,
                    'incorrect_answers': 0,
                }
            )
            
            serializer = UserProgressUpdateSerializer(data=request.data)
            
            if serializer.is_valid():
                is_correct = serializer.validated_data['is_correct']
                
                # Update progress
                progress.times_reviewed += 1
                if is_correct:
                    progress.correct_answers += 1
                    progress.mastery_level = min(progress.mastery_level + 1, 5)
                else:
                    progress.incorrect_answers += 1
                    progress.mastery_level = max(progress.mastery_level - 1, 0)
                
                progress.last_reviewed = timezone.now()
                
                # Calculate next review date based on mastery level
                days_until_next = {
                    0: 1,   # Not started - 1 day
                    1: 3,   # Beginning - 3 days
                    2: 7,   # Developing - 7 days
                    3: 14,  # Competent - 14 days
                    4: 30,  # Proficient - 30 days
                    5: 60,  # Mastered - 60 days
                }
                days = days_until_next.get(progress.mastery_level, 1)
                progress.next_review_date = timezone.now() + timezone.timedelta(days=days)
                
                # Calculate accuracy
                if progress.times_reviewed > 0:
                    progress.accuracy_percentage = (
                        progress.correct_answers / progress.times_reviewed * 100
                    )
                
                progress.save()
                
                response_data = {
                    'mastery_level': progress.mastery_level,
                    'next_review_date': progress.next_review_date,
                    'accuracy_percentage': progress.accuracy_percentage,
                }
                
                return self.success_response(
                    data=response_data,
                    message="Progress updated successfully"
                )
            
            return self.validation_error_response(
                errors=serializer.errors,
                message="Progress update failed"
            )
        
        except Word.DoesNotExist:
            return self.not_found_response(message="Word not found")
        except Exception as e:
            logger.error(f"Error marking progress: {e}")
            return self.error_response(
                message="Progress update failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CollectionsViewSet(viewsets.ViewSet, UserResponseMixin):
    """
    Collections ViewSet
    
    Manage user's custom word collections
    
    Endpoints:
        GET    /api/user/learning/collections/              - List collections
        POST   /api/user/learning/collections/              - Create collection
        GET    /api/user/learning/collections/{id}/         - Get collection details
        PUT    /api/user/learning/collections/{id}/         - Update collection
        DELETE /api/user/learning/collections/{id}/         - Delete collection
        POST   /api/user/learning/collections/{id}/add_word/    - Add word to collection
        DELETE /api/user/learning/collections/{id}/remove_word/ - Remove word
    """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        List all user's collections
        
        Returns:
            {
                "success": true,
                "message": "Collections retrieved successfully",
                "data": [
                    {
                        "id": "col-1",
                        "name": "Daily Vocabulary",
                        "description": "Words I learn daily",
                        "words_count": 25
                    }
                ]
            }
        """
        collections = Collection.objects.filter(user=request.user)
        serializer = CollectionSerializer(collections, many=True)
        return self.success_response(
            data=serializer.data,
            message="Collections retrieved successfully"
        )
    
    def create(self, request):
        """
        Create new collection
        
        Request Body:
            {
                "name": "Daily Vocabulary",
                "description": "Words I learn daily"
            }
        
        Returns:
            {
                "success": true,
                "message": "Collection created successfully",
                "data": {
                    "id": "col-1",
                    "name": "Daily Vocabulary",
                    ...
                }
            }
        """
        serializer = CollectionCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            collection = serializer.save(user=request.user)
            response_serializer = CollectionSerializer(collection)
            return self.success_response(
                data=response_serializer.data,
                message="Collection created successfully",
                status_code=status.HTTP_201_CREATED
            )
        
        return self.validation_error_response(
            errors=serializer.errors,
            message="Collection creation failed"
        )
    
    def retrieve(self, request, pk=None):
        """
        Get collection details with all words
        
        Returns:
            {
                "success": true,
                "message": "Collection retrieved successfully",
                "data": {
                    "id": "col-1",
                    "name": "Daily Vocabulary",
                    "words": [...]
                }
            }
        """
        try:
            collection = Collection.objects.get(id=pk, user=request.user)
            serializer = CollectionSerializer(collection)
            return self.success_response(
                data=serializer.data,
                message="Collection retrieved successfully"
            )
        except Collection.DoesNotExist:
            return self.not_found_response(message="Collection not found")
    
    def update(self, request, pk=None):
        """
        Update collection details
        
        Request Body:
            {
                "name": "Updated Collection Name",
                "description": "Updated description"
            }
        """
        try:
            collection = Collection.objects.get(id=pk, user=request.user)
            serializer = CollectionCreateSerializer(
                collection,
                data=request.data,
                partial=True
            )
            
            if serializer.is_valid():
                serializer.save()
                return self.success_response(
                    data=serializer.data,
                    message="Collection updated successfully"
                )
            
            return self.validation_error_response(
                errors=serializer.errors,
                message="Collection update failed"
            )
        except Collection.DoesNotExist:
            return self.not_found_response(message="Collection not found")
    
    def destroy(self, request, pk=None):
        """
        Delete collection
        
        Returns:
            {
                "success": true,
                "message": "Collection deleted successfully",
                "data": null
            }
        """
        try:
            collection = Collection.objects.get(id=pk, user=request.user)
            collection.delete()
            return self.success_response(
                data=None,
                message="Collection deleted successfully"
            )
        except Collection.DoesNotExist:
            return self.not_found_response(message="Collection not found")
    
    @action(detail=True, methods=['post'], url_path='add_word')
    def add_word(self, request, pk=None):
        """
        Add word to collection
        
        Request Body:
            {
                "word_id": "word-123"
            }
        
        Returns:
            {
                "success": true,
                "message": "Word added to collection successfully",
                "data": null
            }
        """
        try:
            collection = Collection.objects.get(id=pk, user=request.user)
            word_id = request.data.get('word_id')
            
            if not word_id:
                return self.error_response(
                    message="word_id is required",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            word = Word.objects.get(id=word_id)
            
            collection_word, created = CollectionWord.objects.get_or_create(
                collection=collection,
                word=word
            )
            
            if created:
                return self.success_response(
                    data=None,
                    message="Word added to collection successfully",
                    status_code=status.HTTP_201_CREATED
                )
            else:
                return self.error_response(
                    message="Word already in collection",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        except Collection.DoesNotExist:
            return self.not_found_response(message="Collection not found")
        except Word.DoesNotExist:
            return self.not_found_response(message="Word not found")
        except Exception as e:
            logger.error(f"Error adding word to collection: {e}")
            return self.error_response(
                message="Failed to add word",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['delete'], url_path='remove_word')
    def remove_word(self, request, pk=None):
        """
        Remove word from collection
        
        Query Parameters:
            - word_id: Word ID to remove
        
        Returns:
            {
                "success": true,
                "message": "Word removed from collection successfully",
                "data": null
            }
        """
        try:
            collection = Collection.objects.get(id=pk, user=request.user)
            word_id = request.query_params.get('word_id')
            
            if not word_id:
                return self.error_response(
                    message="word_id is required",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            collection_word = CollectionWord.objects.get(
                collection=collection,
                word_id=word_id
            )
            collection_word.delete()
            
            return self.success_response(
                data=None,
                message="Word removed from collection successfully"
            )
        
        except Collection.DoesNotExist:
            return self.not_found_response(message="Collection not found")
        except CollectionWord.DoesNotExist:
            return self.not_found_response(message="Word not in collection")
        except Exception as e:
            logger.error(f"Error removing word from collection: {e}")
            return self.error_response(
                message="Failed to remove word",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
