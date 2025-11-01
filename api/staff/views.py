"""
Staff APIs - Endpoints accessible to staff members
Includes content management, user monitoring, and moderation tools
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta

from apps.accounts.models import User, UserDevice
from apps.vocabulary.models import Language, Word, Collection, CollectionWord, Book, Chapter
from apps.progress.models import UserProgress, UserSession
from apps.versioning.models import AppVersion
from api.base.permissions import StaffRolePermission
from api.base.responses import success_response, error_response, ResponseMixin
import logging

logger = logging.getLogger(__name__)


class StaffDashboardView(APIView, ResponseMixin):
    """
    Staff dashboard with system overview and management tools
    """
    permission_classes = [IsAuthenticated, StaffRolePermission]
    
    def get(self, request):
        """Get staff dashboard data"""
        
        # User statistics
        total_users = User.objects.count()
        active_users_30d = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=30)
        ).count()
        new_users_7d = User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Content statistics
        total_words = Word.objects.count()
        total_collections = Collection.objects.count()
        total_languages = Language.objects.count()
        
        # Learning activity (last 7 days)
        last_week = timezone.now() - timedelta(days=7)
        recent_sessions = UserSession.objects.filter(start_time__gte=last_week)
        total_sessions = recent_sessions.count()
        total_study_time = recent_sessions.aggregate(
            total_minutes=Sum('duration_minutes')
        )['total_minutes'] or 0
        
        # Most active users (last 30 days)
        active_users = User.objects.filter(
            usersession__start_time__gte=timezone.now() - timedelta(days=30)
        ).annotate(
            session_count=Count('usersession'),
            total_minutes=Sum('usersession__duration_minutes')
        ).order_by('-session_count')[:10]
        
        active_users_data = [
            {
                'id': str(user.id),
                'email': user.email,
                'username': user.username,
                'session_count': user.session_count,
                'total_minutes': user.total_minutes or 0,
                'last_login': user.last_login.isoformat() if user.last_login else None,
            }
            for user in active_users
        ]
        
        # Recent user registrations
        recent_users = User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=7)
        ).order_by('-date_joined')[:5]
        
        recent_users_data = [
            {
                'id': str(user.id),
                'email': user.email,
                'username': user.username,
                'date_joined': user.date_joined.isoformat(),
                'auth_provider': user.auth_provider,
            }
            for user in recent_users
        ]
        
        dashboard_data = {
            'user_stats': {
                'total_users': total_users,
                'active_users_30d': active_users_30d,
                'new_users_7d': new_users_7d,
                'retention_rate': round((active_users_30d / total_users) * 100, 1) if total_users > 0 else 0,
            },
            'content_stats': {
                'total_words': total_words,
                'total_collections': total_collections,
                'total_languages': total_languages,
            },
            'activity_stats': {
                'sessions_last_7d': total_sessions,
                'study_time_last_7d': total_study_time,
                'avg_session_length': round(total_study_time / total_sessions, 1) if total_sessions > 0 else 0,
            },
            'most_active_users': active_users_data,
            'recent_registrations': recent_users_data,
        }
        
        return self.success_response(
            data=dashboard_data,
            message="Staff dashboard data retrieved successfully"
        )


class UserManagementView(APIView, ResponseMixin):
    """
    User management for staff - view, search, and moderate users
    """
    permission_classes = [IsAuthenticated, StaffRolePermission]
    
    def get(self, request):
        """Get users with filtering and search"""
        
        # Query parameters
        search = request.query_params.get('search', '')
        auth_provider = request.query_params.get('auth_provider')
        is_active = request.query_params.get('is_active')
        date_joined_from = request.query_params.get('date_joined_from')
        date_joined_to = request.query_params.get('date_joined_to')
        last_login_from = request.query_params.get('last_login_from')
        
        # Base query
        users_query = User.objects.all()
        
        # Apply filters
        if search:
            users_query = users_query.filter(
                Q(email__icontains=search) |
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        if auth_provider:
            users_query = users_query.filter(auth_provider=auth_provider)
        
        if is_active is not None:
            users_query = users_query.filter(is_active=is_active.lower() == 'true')
        
        if date_joined_from:
            users_query = users_query.filter(date_joined__gte=date_joined_from)
        
        if date_joined_to:
            users_query = users_query.filter(date_joined__lte=date_joined_to)
        
        if last_login_from:
            users_query = users_query.filter(last_login__gte=last_login_from)
        
        # Add learning statistics
        users_query = users_query.annotate(
            total_sessions=Count('usersession'),
            total_study_time=Sum('usersession__duration_minutes'),
            words_learned=Count('userprogress')
        ).order_by('-date_joined')
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 25))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = users_query.count()
        users = users_query[start:end]
        
        users_data = []
        for user in users:
            # Get device information
            devices = UserDevice.objects.filter(user=user).values(
                'platform', 'last_sync'
            )
            
            users_data.append({
                'id': str(user.id),
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.full_name,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'auth_provider': user.auth_provider,
                'preferred_language': user.preferred_language,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'learning_stats': {
                    'total_sessions': user.total_sessions or 0,
                    'total_study_time': user.total_study_time or 0,
                    'words_learned': user.words_learned or 0,
                },
                'devices': list(devices),
            })
        
        response_data = {
            'users': users_data,
            'pagination': {
                'current_page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size,
                'has_next': end < total_count,
                'has_previous': page > 1,
            }
        }
        
        return self.success_response(
            data=response_data,
            message="Users retrieved successfully"
        )
    
    def patch(self, request, user_id):
        """Update user status (activate/deactivate)"""
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return self.not_found_response("User not found")
        
        # Staff can only modify is_active status of regular users
        if user.is_staff and not request.user.is_superuser:
            return self.permission_denied_response(
                "Cannot modify staff user accounts"
            )
        
        is_active = request.data.get('is_active')
        if is_active is not None:
            user.is_active = is_active
            user.save(update_fields=['is_active'])
            
            action = "activated" if is_active else "deactivated"
            logger.info(f"Staff {request.user.email} {action} user {user.email}")
            
            return self.success_response(
                message=f"User {action} successfully"
            )
        
        return self.error_response(
            message="No valid updates provided",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ContentManagementView(APIView, ResponseMixin):
    """
    Content management for staff - words, collections, and books
    """
    permission_classes = [IsAuthenticated, StaffRolePermission]
    
    def get(self, request):
        """Get content statistics and recent additions"""
        
        # Content statistics by language
        language_stats = Language.objects.annotate(
            word_count=Count('word'),
            collection_count=Count('collection')
        ).order_by('-word_count')
        
        language_data = [
            {
                'id': str(lang.id),
                'name': lang.name,
                'code': lang.code,
                'word_count': lang.word_count,
                'collection_count': lang.collection_count,
            }
            for lang in language_stats
        ]
        
        # Recent words added (last 7 days)
        recent_words = Word.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).select_related('language', 'difficulty_level').order_by('-created_at')[:10]
        
        recent_words_data = [
            {
                'id': str(word.id),
                'word': word.word,
                'language': word.language.name,
                'difficulty_level': word.difficulty_level.level if word.difficulty_level else None,
                'created_at': word.created_at.isoformat(),
            }
            for word in recent_words
        ]
        
        # Recent collections
        recent_collections = Collection.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')[:5]
        
        recent_collections_data = [
            {
                'id': str(collection.id),
                'name': collection.name,
                'category': collection.category,
                'word_count': collection.collectionword_set.count(),
                'created_at': collection.created_at.isoformat(),
            }
            for collection in recent_collections
        ]
        
        # Content quality metrics
        words_without_translations = Word.objects.filter(
            wordtranslation__isnull=True
        ).count()
        
        words_without_definitions = Word.objects.filter(
            worddefinition__isnull=True
        ).count()
        
        content_data = {
            'language_statistics': language_data,
            'recent_words': recent_words_data,
            'recent_collections': recent_collections_data,
            'quality_metrics': {
                'words_without_translations': words_without_translations,
                'words_without_definitions': words_without_definitions,
                'total_words': Word.objects.count(),
            }
        }
        
        return self.success_response(
            data=content_data,
            message="Content management data retrieved successfully"
        )


class LearningAnalyticsView(APIView, ResponseMixin):
    """
    Learning analytics for staff - insights into user learning patterns
    """
    permission_classes = [IsAuthenticated, StaffRolePermission]
    
    def get(self, request):
        """Get learning analytics and trends"""
        
        # Time range
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Daily session statistics
        daily_sessions = UserSession.objects.filter(
            start_time__gte=start_date
        ).extra(
            select={'day': 'DATE(start_time)'}
        ).values('day').annotate(
            session_count=Count('id'),
            total_minutes=Sum('duration_minutes'),
            unique_users=Count('user', distinct=True),
            avg_accuracy=Avg('accuracy_percentage')
        ).order_by('day')
        
        daily_data = [
            {
                'date': item['day'],
                'sessions': item['session_count'],
                'total_minutes': item['total_minutes'] or 0,
                'unique_users': item['unique_users'],
                'avg_accuracy': round(item['avg_accuracy'] or 0, 1),
            }
            for item in daily_sessions
        ]
        
        # Language popularity
        language_popularity = Language.objects.annotate(
            learner_count=Count('word__user_progress__user', distinct=True),
            total_sessions=Count('word__user_progress__user__usersession')
        ).order_by('-learner_count')[:10]
        
        language_data = [
            {
                'language': lang.name,
                'learner_count': lang.learner_count,
                'total_sessions': lang.total_sessions,
            }
            for lang in language_popularity
        ]
        
        # Most challenging words (lowest accuracy)
        challenging_words = Word.objects.filter(
            user_progress__user_session__start_time__gte=start_date
        ).annotate(
            avg_accuracy=Avg('user_progress__user_session__accuracy_percentage'),
            attempt_count=Count('user_progress__user_session')
        ).filter(attempt_count__gte=10).order_by('avg_accuracy')[:10]
        
        challenging_data = [
            {
                'word': word.word,
                'language': word.language.name,
                'avg_accuracy': round(word.avg_accuracy or 0, 1),
                'attempt_count': word.attempt_count,
            }
            for word in challenging_words
        ]
        
        # User engagement patterns
        engagement_stats = UserSession.objects.filter(
            start_time__gte=start_date
        ).aggregate(
            avg_session_length=Avg('duration_minutes'),
            total_sessions=Count('id'),
            total_users=Count('user', distinct=True),
            avg_sessions_per_user=Count('id') / Count('user', distinct=True)
        )
        
        analytics_data = {
            'time_range_days': days,
            'daily_trends': daily_data,
            'language_popularity': language_data,
            'challenging_words': challenging_data,
            'engagement_summary': {
                'avg_session_length': round(engagement_stats['avg_session_length'] or 0, 1),
                'total_sessions': engagement_stats['total_sessions'],
                'total_active_users': engagement_stats['total_users'],
                'avg_sessions_per_user': round(engagement_stats['avg_sessions_per_user'] or 0, 1),
            }
        }
        
        return self.success_response(
            data=analytics_data,
            message="Learning analytics retrieved successfully"
        )


class SystemHealthView(APIView, ResponseMixin):
    """
    System health monitoring for staff
    """
    permission_classes = [IsAuthenticated, StaffRolePermission]
    
    def get(self, request):
        """Get system health metrics"""
        
        # Database statistics
        db_stats = {
            'users': User.objects.count(),
            'words': Word.objects.count(),
            'collections': Collection.objects.count(),
            'user_progress_records': UserProgress.objects.count(),
            'sessions': UserSession.objects.count(),
        }
        
        # Recent activity (last 24 hours)
        last_24h = timezone.now() - timedelta(hours=24)
        recent_activity = {
            'new_users': User.objects.filter(date_joined__gte=last_24h).count(),
            'active_users': User.objects.filter(last_login__gte=last_24h).count(),
            'new_sessions': UserSession.objects.filter(start_time__gte=last_24h).count(),
            'total_study_time': UserSession.objects.filter(
                start_time__gte=last_24h
            ).aggregate(
                total=Sum('duration_minutes')
            )['total'] or 0,
        }
        
        # Error indicators (these would need proper error tracking)
        error_indicators = {
            'failed_logins_24h': 0,  # Would need proper logging
            'api_errors_24h': 0,     # Would need proper error tracking
            'performance_issues': 0,  # Would need monitoring
        }
        
        # App version distribution
        app_versions = UserDevice.objects.values('app_version').annotate(
            device_count=Count('id')
        ).order_by('-device_count')
        
        version_data = [
            {
                'version': item['app_version'] or 'Unknown',
                'device_count': item['device_count'],
            }
            for item in app_versions[:10]
        ]
        
        health_data = {
            'database_stats': db_stats,
            'recent_activity': recent_activity,
            'error_indicators': error_indicators,
            'app_version_distribution': version_data,
            'system_status': 'healthy',  # Would be calculated based on various metrics
            'last_updated': timezone.now().isoformat(),
        }
        
        return self.success_response(
            data=health_data,
            message="System health data retrieved successfully"
        )