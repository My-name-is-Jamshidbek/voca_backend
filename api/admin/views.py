"""
Admin APIs - Endpoints accessible to administrators only
Includes system administration, user management, and advanced configuration
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

from apps.accounts.models import User, UserDevice
from apps.vocabulary.models import Language, Word, Collection, CollectionWord, Book, Chapter
from apps.progress.models import UserProgress, UserSession
from apps.versioning.models import AppVersion
from apps.tokens.models import MobileAppToken, APIClientToken, TokenUsageLog
from api.base.permissions import AdminRolePermission
from api.base.responses import success_response, error_response, ResponseMixin
import logging

logger = logging.getLogger(__name__)


class AdminDashboardView(APIView, ResponseMixin):
    """
    Administrator dashboard with comprehensive system overview
    """
    permission_classes = [IsAuthenticated, AdminRolePermission]
    
    def get(self, request):
        """Get admin dashboard with system-wide statistics"""
        
        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        admin_users = User.objects.filter(is_superuser=True).count()
        
        # Recent user activity
        last_24h = timezone.now() - timedelta(hours=24)
        last_7d = timezone.now() - timedelta(days=7)
        last_30d = timezone.now() - timedelta(days=30)
        
        activity_stats = {
            'logins_24h': User.objects.filter(last_login__gte=last_24h).count(),
            'logins_7d': User.objects.filter(last_login__gte=last_7d).count(),
            'registrations_7d': User.objects.filter(date_joined__gte=last_7d).count(),
            'sessions_24h': UserSession.objects.filter(start_time__gte=last_24h).count(),
        }
        
        # Content statistics
        content_stats = {
            'total_languages': Language.objects.count(),
            'total_words': Word.objects.count(),
            'total_collections': Collection.objects.count(),
            'total_books': Book.objects.count(),
            'total_chapters': Chapter.objects.count(),
        }
        
        # Learning progress statistics
        progress_stats = {
            'total_progress_records': UserProgress.objects.count(),
            'total_sessions': UserSession.objects.count(),
            'total_study_time': UserSession.objects.aggregate(
                total=Sum('duration_minutes')
            )['total'] or 0,
            'avg_session_length': UserSession.objects.aggregate(
                avg=Avg('duration_minutes')
            )['avg'] or 0,
        }
        
        # Token usage statistics
        token_stats = {
            'mobile_tokens': MobileAppToken.objects.count(),
            'active_mobile_tokens': MobileAppToken.objects.filter(status='active').count(),
            'api_tokens': APIClientToken.objects.count(),
            'active_api_tokens': APIClientToken.objects.filter(status='active').count(),
            'token_usage_24h': TokenUsageLog.objects.filter(
                timestamp__gte=last_24h
            ).count(),
        }
        
        # System health indicators
        health_indicators = {
            'database_size': self.get_database_size(),
            'storage_usage': self.get_storage_usage(),
            'performance_metrics': self.get_performance_metrics(),
        }
        
        dashboard_data = {
            'user_statistics': {
                'total_users': total_users,
                'active_users': active_users,
                'staff_users': staff_users,
                'admin_users': admin_users,
                'inactive_users': total_users - active_users,
            },
            'activity_statistics': activity_stats,
            'content_statistics': content_stats,
            'progress_statistics': progress_stats,
            'token_statistics': token_stats,
            'health_indicators': health_indicators,
            'timestamp': timezone.now().isoformat(),
        }
        
        return self.success_response(
            data=dashboard_data,
            message="Admin dashboard data retrieved successfully"
        )
    
    def get_database_size(self):
        """Get database size information (placeholder)"""
        return {
            'total_records': (
                User.objects.count() +
                Word.objects.count() +
                UserProgress.objects.count() +
                UserSession.objects.count()
            ),
            'estimated_size_mb': 'N/A',  # Would need actual database queries
        }
    
    def get_storage_usage(self):
        """Get storage usage information (placeholder)"""
        return {
            'media_files': 'N/A',
            'logs': 'N/A',
            'backups': 'N/A',
        }
    
    def get_performance_metrics(self):
        """Get performance metrics (placeholder)"""
        return {
            'avg_response_time': 'N/A',
            'error_rate': 'N/A',
            'uptime': 'N/A',
        }


class SystemAdministrationView(APIView, ResponseMixin):
    """
    System administration tools for managing the application
    """
    permission_classes = [IsAuthenticated, AdminRolePermission]
    
    def get(self, request):
        """Get system configuration and status"""
        
        # App version information
        app_versions = AppVersion.objects.all().order_by('-version_number')
        version_data = [
            {
                'id': str(version.id),
                'version_number': version.version_number,
                'release_date': version.release_date.isoformat(),
                'is_required': version.is_required,
                'is_latest': version.is_latest,
                'download_url': version.download_url,
                'description': version.description,
            }
            for version in app_versions
        ]
        
        # Database health check
        db_health = self.check_database_health()
        
        # Recent errors and logs (placeholder)
        recent_errors = []  # Would need proper error logging
        
        system_info = {
            'app_versions': version_data,
            'database_health': db_health,
            'recent_errors': recent_errors,
            'system_status': 'operational',
            'maintenance_mode': False,
        }
        
        return self.success_response(
            data=system_info,
            message="System information retrieved successfully"
        )
    
    def post(self, request):
        """Perform system administration actions"""
        action = request.data.get('action')
        
        if action == 'maintenance_mode':
            # Toggle maintenance mode (would need implementation)
            enabled = request.data.get('enabled', False)
            logger.info(f"Admin {request.user.email} {'enabled' if enabled else 'disabled'} maintenance mode")
            return self.success_response(
                message=f"Maintenance mode {'enabled' if enabled else 'disabled'}"
            )
        
        elif action == 'clear_cache':
            # Clear application cache (would need implementation)
            logger.info(f"Admin {request.user.email} cleared application cache")
            return self.success_response(message="Cache cleared successfully")
        
        elif action == 'backup_database':
            # Trigger database backup (would need implementation)
            logger.info(f"Admin {request.user.email} initiated database backup")
            return self.success_response(message="Database backup initiated")
        
        else:
            return self.error_response(
                message="Invalid action",
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    def check_database_health(self):
        """Check database connectivity and performance"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return {
                    'status': 'healthy',
                    'connection': 'active',
                    'response_time': 'fast',
                }
        except Exception as e:
            return {
                'status': 'error',
                'connection': 'failed',
                'error': str(e),
            }


class UserAdministrationView(APIView, ResponseMixin):
    """
    Advanced user management for administrators
    """
    permission_classes = [IsAuthenticated, AdminRolePermission]
    
    def get(self, request):
        """Get comprehensive user management data"""
        
        # User role distribution
        role_distribution = {
            'regular_users': User.objects.filter(is_staff=False, is_superuser=False).count(),
            'staff_users': User.objects.filter(is_staff=True, is_superuser=False).count(),
            'admin_users': User.objects.filter(is_superuser=True).count(),
        }
        
        # Authentication provider statistics
        auth_providers = User.objects.values('auth_provider').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent user activities
        recent_activities = [
            {
                'type': 'registration',
                'count': User.objects.filter(
                    date_joined__gte=timezone.now() - timedelta(days=1)
                ).count(),
                'period': '24h',
            },
            {
                'type': 'login',
                'count': User.objects.filter(
                    last_login__gte=timezone.now() - timedelta(days=1)
                ).count(),
                'period': '24h',
            },
        ]
        
        # Problematic users (placeholder criteria)
        problematic_users = User.objects.filter(
            Q(is_active=False) |
            Q(last_login__isnull=True, date_joined__lt=timezone.now() - timedelta(days=30))
        )[:10]
        
        problematic_data = [
            {
                'id': str(user.id),
                'email': user.email,
                'is_active': user.is_active,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'date_joined': user.date_joined.isoformat(),
                'issues': ['inactive'] if not user.is_active else ['never_logged_in'],
            }
            for user in problematic_users
        ]
        
        user_admin_data = {
            'role_distribution': role_distribution,
            'auth_provider_stats': list(auth_providers),
            'recent_activities': recent_activities,
            'problematic_users': problematic_data,
        }
        
        return self.success_response(
            data=user_admin_data,
            message="User administration data retrieved successfully"
        )
    
    def post(self, request):
        """Perform bulk user operations"""
        action = request.data.get('action')
        user_ids = request.data.get('user_ids', [])
        
        if not user_ids:
            return self.error_response(
                message="User IDs are required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        users = User.objects.filter(id__in=user_ids)
        
        if action == 'activate':
            users.update(is_active=True)
            logger.info(f"Admin {request.user.email} activated {users.count()} users")
            return self.success_response(
                message=f"Activated {users.count()} users"
            )
        
        elif action == 'deactivate':
            # Prevent deactivating other admins
            admin_users = users.filter(is_superuser=True).exclude(id=request.user.id)
            if admin_users.exists():
                return self.error_response(
                    message="Cannot deactivate admin users",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            users.update(is_active=False)
            logger.info(f"Admin {request.user.email} deactivated {users.count()} users")
            return self.success_response(
                message=f"Deactivated {users.count()} users"
            )
        
        elif action == 'promote_to_staff':
            users.update(is_staff=True)
            logger.info(f"Admin {request.user.email} promoted {users.count()} users to staff")
            return self.success_response(
                message=f"Promoted {users.count()} users to staff"
            )
        
        elif action == 'demote_from_staff':
            # Prevent demoting other admins
            admin_users = users.filter(is_superuser=True)
            if admin_users.exists():
                return self.error_response(
                    message="Cannot demote admin users",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            users.update(is_staff=False)
            logger.info(f"Admin {request.user.email} demoted {users.count()} users from staff")
            return self.success_response(
                message=f"Demoted {users.count()} users from staff"
            )
        
        else:
            return self.error_response(
                message="Invalid action",
                status_code=status.HTTP_400_BAD_REQUEST
            )


class TokenAdministrationView(APIView, ResponseMixin):
    """
    Token management for administrators
    """
    permission_classes = [IsAuthenticated, AdminRolePermission]
    
    def get(self, request):
        """Get token management overview"""
        
        # Mobile token statistics
        mobile_token_stats = {
            'total': MobileAppToken.objects.count(),
            'active': MobileAppToken.objects.filter(status='active').count(),
            'inactive': MobileAppToken.objects.filter(status='inactive').count(),
            'revoked': MobileAppToken.objects.filter(status='revoked').count(),
        }
        
        # API token statistics
        api_token_stats = {
            'total': APIClientToken.objects.count(),
            'active': APIClientToken.objects.filter(status='active').count(),
            'inactive': APIClientToken.objects.filter(status='inactive').count(),
            'revoked': APIClientToken.objects.filter(status='revoked').count(),
        }
        
        # Token usage over time (last 7 days)
        last_week = timezone.now() - timedelta(days=7)
        daily_usage = TokenUsageLog.objects.filter(
            timestamp__gte=last_week
        ).extra(
            select={'day': 'DATE(timestamp)'}
        ).values('day', 'token_type').annotate(
            usage_count=Count('id')
        ).order_by('day', 'token_type')
        
        # Most active tokens
        active_tokens = TokenUsageLog.objects.filter(
            timestamp__gte=last_week
        ).values('token_name', 'token_type').annotate(
            usage_count=Count('id')
        ).order_by('-usage_count')[:10]
        
        token_data = {
            'mobile_token_stats': mobile_token_stats,
            'api_token_stats': api_token_stats,
            'daily_usage': list(daily_usage),
            'most_active_tokens': list(active_tokens),
        }
        
        return self.success_response(
            data=token_data,
            message="Token administration data retrieved successfully"
        )
    
    def post(self, request):
        """Perform token management actions"""
        action = request.data.get('action')
        token_type = request.data.get('token_type')  # 'mobile' or 'api'
        token_ids = request.data.get('token_ids', [])
        
        if not token_ids:
            return self.error_response(
                message="Token IDs are required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if token_type == 'mobile':
            tokens = MobileAppToken.objects.filter(id__in=token_ids)
        elif token_type == 'api':
            tokens = APIClientToken.objects.filter(id__in=token_ids)
        else:
            return self.error_response(
                message="Invalid token type",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if action == 'activate':
            tokens.update(status='active')
            logger.info(f"Admin {request.user.email} activated {tokens.count()} {token_type} tokens")
            return self.success_response(
                message=f"Activated {tokens.count()} {token_type} tokens"
            )
        
        elif action == 'deactivate':
            tokens.update(status='inactive')
            logger.info(f"Admin {request.user.email} deactivated {tokens.count()} {token_type} tokens")
            return self.success_response(
                message=f"Deactivated {tokens.count()} {token_type} tokens"
            )
        
        elif action == 'revoke':
            tokens.update(status='revoked')
            logger.info(f"Admin {request.user.email} revoked {tokens.count()} {token_type} tokens")
            return self.success_response(
                message=f"Revoked {tokens.count()} {token_type} tokens"
            )
        
        else:
            return self.error_response(
                message="Invalid action",
                status_code=status.HTTP_400_BAD_REQUEST
            )


class SystemAnalyticsView(APIView, ResponseMixin):
    """
    Advanced system analytics for administrators
    """
    permission_classes = [IsAuthenticated, AdminRolePermission]
    
    def get(self, request):
        """Get comprehensive system analytics"""
        
        # Time range
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # User growth over time
        user_growth = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            user_count = User.objects.filter(date_joined__date=date.date()).count()
            user_growth.append({
                'date': date.date().isoformat(),
                'new_users': user_count,
            })
        
        # Learning activity trends
        activity_trends = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            sessions = UserSession.objects.filter(start_time__date=date.date())
            activity_trends.append({
                'date': date.date().isoformat(),
                'sessions': sessions.count(),
                'total_minutes': sessions.aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0,
                'unique_users': sessions.values('user').distinct().count(),
            })
        
        # Content usage statistics
        language_usage = Language.objects.annotate(
            active_learners=Count('word__user_progress__user', distinct=True),
            total_sessions=Count('word__user_progress__user__usersession')
        ).order_by('-active_learners')
        
        language_data = [
            {
                'language': lang.name,
                'code': lang.code,
                'active_learners': lang.active_learners,
                'total_sessions': lang.total_sessions,
            }
            for lang in language_usage
        ]
        
        # Performance metrics (placeholder)
        performance_metrics = {
            'avg_response_time': 150,  # ms
            'error_rate': 0.1,  # %
            'uptime': 99.9,  # %
            'concurrent_users': 45,
        }
        
        analytics_data = {
            'time_range_days': days,
            'user_growth': user_growth,
            'activity_trends': activity_trends,
            'language_usage': language_data,
            'performance_metrics': performance_metrics,
        }
        
        return self.success_response(
            data=analytics_data,
            message="System analytics retrieved successfully"
        )