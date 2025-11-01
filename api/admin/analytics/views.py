"""
Admin Analytics API - System analytics and reporting for admins
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.db.models import Count, Avg, Q
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.vocabulary.models import Category, Word
from apps.quizzes.models import Quiz, QuizAttempt
from apps.accounts.models import User
from ...base import AdminRolePermission, success_response, error_response
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class AdminAnalyticsViewSet(viewsets.ViewSet):
    """
    Admin analytics and reporting APIs
    """
    permission_classes = [permissions.IsAuthenticated, AdminRolePermission]
    
    @action(detail=False, methods=['get'])
    def system_health(self, request):
        """Get system health metrics"""
        from django.db import connection
        from django.conf import settings
        
        # Database stats
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")  # Simple health check
            db_status = "healthy"
        
        # Application stats
        health_data = {
            'database': {
                'status': db_status,
                'total_collections': 5,  # Approximate for MongoDB
            },
            'application': {
                'debug_mode': settings.DEBUG,
                'total_users': User.objects.count(),
                'total_content_items': (
                    Category.objects.count() + 
                    Word.objects.count() + 
                    Quiz.objects.count()
                ),
            },
            'performance': {
                'active_quiz_attempts': QuizAttempt.objects.filter(status='in_progress').count(),
                'completed_quizzes_today': QuizAttempt.objects.filter(
                    completed_at__date=timezone.now().date(),
                    status='completed'
                ).count(),
            }
        }
        
        return success_response(
            data=health_data,
            message="System health metrics retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def usage_analytics(self, request):
        """Get detailed usage analytics"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Date ranges
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        analytics = {
            'user_activity': {
                'new_users_today': User.objects.filter(created_at__date=today).count(),
                'new_users_week': User.objects.filter(created_at__date__gte=week_ago).count(),
                'new_users_month': User.objects.filter(created_at__date__gte=month_ago).count(),
            },
            'learning_activity': {
                'quizzes_taken_today': QuizAttempt.objects.filter(started_at__date=today).count(),
                'quizzes_taken_week': QuizAttempt.objects.filter(started_at__date__gte=week_ago).count(),
                'quizzes_taken_month': QuizAttempt.objects.filter(started_at__date__gte=month_ago).count(),
            },
            'content_creation': {
                'words_added_week': Word.objects.filter(created_at__date__gte=week_ago).count(),
                'categories_added_week': Category.objects.filter(created_at__date__gte=week_ago).count(),
                'quizzes_added_week': Quiz.objects.filter(created_at__date__gte=week_ago).count(),
            },
            'top_performers': {
                'most_active_users': User.objects.annotate(
                    quiz_count=Count('quiz_attempts')
                ).filter(
                    role='user',
                    quiz_count__gt=0
                ).order_by('-quiz_count')[:5].values('email', 'quiz_count'),
                
                'popular_categories': Category.objects.annotate(
                    word_count=Count('words'),
                    quiz_count=Count('quizzes')
                ).order_by('-word_count')[:5].values('name', 'word_count', 'quiz_count'),
            }
        }
        
        return success_response(
            data=analytics,
            message="Usage analytics retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def content_overview(self, request):
        """Get content overview statistics"""
        overview = {
            'categories': {
                'total': Category.objects.count(),
                'active': Category.objects.filter(is_active=True).count(),
            },
            'words': {
                'total': Word.objects.count(),
                'active': Word.objects.filter(is_active=True).count(),
                'by_difficulty': {
                    'beginner': Word.objects.filter(difficulty='beginner').count(),
                    'intermediate': Word.objects.filter(difficulty='intermediate').count(),
                    'advanced': Word.objects.filter(difficulty='advanced').count(),
                }
            },
            'quizzes': {
                'total': Quiz.objects.count(),
                'active': Quiz.objects.filter(is_active=True).count(),
                'by_type': {
                    'multiple_choice': Quiz.objects.filter(quiz_type='multiple_choice').count(),
                    'fill_blank': Quiz.objects.filter(quiz_type='fill_blank').count(),
                    'matching': Quiz.objects.filter(quiz_type='matching').count(),
                    'true_false': Quiz.objects.filter(quiz_type='true_false').count(),
                }
            }
        }
        
        return success_response(
            data=overview,
            message="Content overview retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def learning_progress_report(self, request):
        """Get detailed learning progress analytics"""
        from apps.vocabulary.models import UserWordProgress
        
        progress_stats = {
            'overall_progress': {
                'total_learning_sessions': UserWordProgress.objects.count(),
                'words_in_progress': UserWordProgress.objects.filter(status='learning').count(),
                'words_mastered': UserWordProgress.objects.filter(status='mastered').count(),
                'average_review_count': UserWordProgress.objects.aggregate(
                    avg_reviews=Avg('times_reviewed')
                )['avg_reviews'] or 0,
            },
            'user_engagement': {
                'active_learners': User.objects.filter(
                    word_progress__last_reviewed__gte=timezone.now() - timedelta(days=7)
                ).distinct().count(),
                'quiz_completion_rate': self._calculate_quiz_completion_rate(),
            },
            'difficulty_analysis': {
                'beginner_completion': self._get_difficulty_completion('beginner'),
                'intermediate_completion': self._get_difficulty_completion('intermediate'),
                'advanced_completion': self._get_difficulty_completion('advanced'),
            }
        }
        
        return success_response(
            data=progress_stats,
            message="Learning progress report retrieved successfully"
        )
    
    def _calculate_quiz_completion_rate(self):
        """Calculate quiz completion rate"""
        total_attempts = QuizAttempt.objects.count()
        completed_attempts = QuizAttempt.objects.filter(status='completed').count()
        
        if total_attempts == 0:
            return 0
        
        return round((completed_attempts / total_attempts) * 100, 2)
    
    def _get_difficulty_completion(self, difficulty):
        """Get completion rate for specific difficulty level"""
        from apps.vocabulary.models import UserWordProgress
        
        total_words = Word.objects.filter(difficulty=difficulty).count()
        mastered_progress = UserWordProgress.objects.filter(
            word__difficulty=difficulty,
            status='mastered'
        ).count()
        
        if total_words == 0:
            return 0
        
        return round((mastered_progress / total_words) * 100, 2)