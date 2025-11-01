"""
Admin Vocabulary API - Vocabulary management for admins
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.db.models import Count
from apps.vocabulary.models import Category, Word, UserWordProgress
from ...base import AdminRolePermission, success_response, error_response
from ...cruds.serializers import CategorySerializer, WordSerializer
import logging

logger = logging.getLogger(__name__)


class AdminCategoryViewSet(viewsets.ModelViewSet):
    """
    Admin API for managing categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, AdminRolePermission]
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get category statistics"""
        stats = {
            'total_categories': Category.objects.count(),
            'active_categories': Category.objects.filter(is_active=True).count(),
            'categories_with_words': Category.objects.annotate(
                word_count=Count('words')
            ).filter(word_count__gt=0).count(),
            'most_popular': Category.objects.annotate(
                word_count=Count('words')
            ).order_by('-word_count')[:5].values('name', 'word_count')
        }
        
        return success_response(
            data=stats,
            message="Category statistics retrieved successfully"
        )
    
    @action(detail=False, methods=['post'])
    def bulk_operations(self, request):
        """Perform bulk operations on categories"""
        operation = request.data.get('operation')
        ids = request.data.get('ids', [])
        
        if not operation or not ids:
            return error_response(
                message="Operation and ids are required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if operation == 'activate':
            updated = Category.objects.filter(id__in=ids).update(is_active=True)
        elif operation == 'deactivate':
            updated = Category.objects.filter(id__in=ids).update(is_active=False)
        elif operation == 'delete':
            updated = Category.objects.filter(id__in=ids).delete()[0]
        else:
            return error_response(
                message="Invalid operation",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return success_response(
            data={'updated_count': updated},
            message=f"Bulk {operation} completed successfully"
        )


class AdminWordViewSet(viewsets.ModelViewSet):
    """
    Admin API for managing words
    """
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    permission_classes = [permissions.IsAuthenticated, AdminRolePermission]
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get word statistics"""
        stats = {
            'total_words': Word.objects.count(),
            'active_words': Word.objects.filter(is_active=True).count(),
            'by_difficulty': {
                'beginner': Word.objects.filter(difficulty='beginner').count(),
                'intermediate': Word.objects.filter(difficulty='intermediate').count(),
                'advanced': Word.objects.filter(difficulty='advanced').count(),
            },
            'by_category': Word.objects.values('category__name').annotate(
                count=Count('id')
            ).order_by('-count')[:10],
            'learning_progress': {
                'words_being_learned': UserWordProgress.objects.filter(
                    status='learning'
                ).count(),
                'words_mastered': UserWordProgress.objects.filter(
                    status='mastered'
                ).count(),
            }
        }
        
        return success_response(
            data=stats,
            message="Word statistics retrieved successfully"
        )
    
    @action(detail=False, methods=['post'])
    def bulk_operations(self, request):
        """Perform bulk operations on words"""
        operation = request.data.get('operation')
        ids = request.data.get('ids', [])
        
        if not operation or not ids:
            return error_response(
                message="Operation and ids are required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if operation == 'activate':
            updated = Word.objects.filter(id__in=ids).update(is_active=True)
        elif operation == 'deactivate':
            updated = Word.objects.filter(id__in=ids).update(is_active=False)
        elif operation == 'delete':
            updated = Word.objects.filter(id__in=ids).delete()[0]
        elif operation == 'change_difficulty':
            new_difficulty = request.data.get('difficulty')
            if new_difficulty in ['beginner', 'intermediate', 'advanced']:
                updated = Word.objects.filter(id__in=ids).update(difficulty=new_difficulty)
            else:
                return error_response(
                    message="Invalid difficulty level",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        else:
            return error_response(
                message="Invalid operation",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return success_response(
            data={'updated_count': updated},
            message=f"Bulk {operation} completed successfully"
        )
    
    @action(detail=False, methods=['post'])
    def import_words(self, request):
        """Bulk import words from file"""
        # This would handle CSV/JSON import
        # Implementation depends on file format requirements
        return success_response(
            message="Word import functionality - to be implemented"
        )