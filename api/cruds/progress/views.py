"""
ViewSets for Progress App Models
"""
from rest_framework import status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Avg

from apps.progress.models import UserProgress, UserSession
from ..common.base import BaseModelViewSet
from .serializers import UserProgressSerializer, UserSessionSerializer
from ...base import success_response, error_response


class UserProgressViewSet(BaseModelViewSet):
    """CRUD operations for UserProgress model"""
    serializer_class = UserProgressSerializer
    filterset_fields = ['status', 'word__language', 'word__difficulty_level']
    ordering = ['-last_reviewed']
    
    def get_queryset(self):
        """Filter progress based on user permissions"""
        queryset = UserProgress.objects.select_related('user', 'word').all()
        
        # Users can only see their own progress
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def due_for_review(self, request):
        """Get words due for review"""
        now = timezone.now()
        due_words = self.get_queryset().filter(next_review__lte=now)
        serializer = self.get_serializer(due_words, many=True)
        return success_response(
            data=serializer.data,
            message="Words due for review retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get user progress statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_words': queryset.count(),
            'learned_words': queryset.filter(status='learned').count(),
            'learning_words': queryset.filter(status='learning').count(),
            'new_words': queryset.filter(status='new').count(),
            'average_accuracy': queryset.aggregate(
                avg_accuracy=Avg('times_correct') * 100.0 / Avg('times_reviewed')
            )['avg_accuracy'] or 0,
            'words_due_today': queryset.filter(
                next_review__date=timezone.now().date()
            ).count()
        }
        
        return success_response(
            data=stats,
            message="Progress statistics retrieved successfully"
        )
    
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
    """CRUD operations for UserSession model"""
    serializer_class = UserSessionSerializer
    filterset_fields = ['user', 'session_date']
    ordering_fields = ['session_date', 'created_at']
    ordering = ['-session_date']
    
    def get_queryset(self):
        """Filter sessions based on user permissions"""
        queryset = UserSession.objects.select_related('user').all()
        
        # Users can only see their own sessions
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
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
    
    @action(detail=False, methods=['get'])
    def weekly_stats(self, request):
        """Get weekly session statistics"""
        from datetime import timedelta
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)
        
        sessions = self.get_queryset().filter(
            session_date__range=[start_date, end_date]
        )
        
        stats = {
            'total_sessions': sessions.count(),
            'total_words_learned': sum(s.words_learned for s in sessions),
            'total_words_reviewed': sum(s.words_reviewed for s in sessions),
            'total_time_minutes': sum(s.total_time_minutes for s in sessions),
            'daily_breakdown': []
        }
        
        # Daily breakdown
        for i in range(7):
            date = start_date + timedelta(days=i)
            day_sessions = sessions.filter(session_date=date)
            stats['daily_breakdown'].append({
                'date': date,
                'sessions': day_sessions.count(),
                'words_learned': sum(s.words_learned for s in day_sessions),
                'words_reviewed': sum(s.words_reviewed for s in day_sessions),
                'time_minutes': sum(s.total_time_minutes for s in day_sessions)
            })
        
        return success_response(
            data=stats,
            message="Weekly statistics retrieved successfully"
        )