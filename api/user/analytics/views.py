"""
User Analytics Views
Learning statistics, performance analytics, and progress reports
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from django.db.models import Sum, Avg, Q, Count
from apps.progress.models import UserProgress, UserSession
from apps.vocabulary.models import DifficultyLevel
from ..common import UserResponseMixin, calculate_learning_stats, calculate_streak
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


class AnalyticsViewSet(viewsets.ViewSet, UserResponseMixin):
    """
    Analytics ViewSet
    
    Comprehensive learning analytics and performance reporting
    Requires Bearer token authentication
    
    Endpoints:
        GET    /api/user/analytics/overview/           - Learning overview
        GET    /api/user/analytics/progress/           - Learning progress details
        GET    /api/user/analytics/daily/              - Daily statistics
        GET    /api/user/analytics/weekly/             - Weekly statistics
        GET    /api/user/analytics/monthly/            - Monthly statistics
        GET    /api/user/analytics/difficulty/         - Stats by difficulty level
        GET    /api/user/analytics/sessions/           - Study sessions history
        GET    /api/user/analytics/performance/        - Performance metrics
    """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='overview')
    def overview(self, request):
        """
        Get learning overview
        
        Returns:
            {
                "success": true,
                "message": "Overview retrieved successfully",
                "data": {
                    "stats": {
                        "total_words_available": 5000,
                        "words_learned": 250,
                        "words_in_progress": 150,
                        "learning_percentage": 5.0
                    },
                    "streak": {
                        "current_streak": 7,
                        "longest_streak": 15
                    },
                    "today_session": {
                        "duration_minutes": 30,
                        "words_reviewed": 10,
                        "accuracy_percentage": 85.0
                    }
                }
            }
        """
        try:
            stats = calculate_learning_stats(request.user)
            streak = calculate_streak(request.user)
            
            # Today's session
            today = timezone.now().date()
            today_session = UserSession.objects.filter(
                user=request.user,
                session_date=today
            ).aggregate(
                duration_minutes=Sum('duration_minutes'),
                words_reviewed=Sum('words_reviewed'),
                accuracy_percentage=Avg('accuracy_percentage')
            )
            
            response_data = {
                'stats': stats,
                'streak': streak,
                'today_session': {
                    'duration_minutes': today_session['duration_minutes'] or 0,
                    'words_reviewed': today_session['words_reviewed'] or 0,
                    'accuracy_percentage': today_session['accuracy_percentage'] or 0,
                }
            }
            
            return self.success_response(
                data=response_data,
                message="Overview retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Error getting overview: {e}")
            return self.error_response(
                message="Failed to retrieve overview",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='progress')
    def progress(self, request):
        """
        Get detailed learning progress
        
        Query Parameters:
            - days: Number of days to include (default: 30)
        
        Returns:
            {
                "success": true,
                "message": "Progress retrieved successfully",
                "data": {
                    "mastery_distribution": {
                        "0": 1000,
                        "1": 800,
                        "2": 600,
                        "3": 400,
                        "4": 150,
                        "5": 50
                    },
                    "difficulty_progress": [
                        {
                            "level": "A1",
                            "total": 500,
                            "learned": 250,
                            "percentage": 50
                        }
                    ]
                }
            }
        """
        try:
            days = int(request.query_params.get('days', 30))
            
            # Mastery distribution
            progress_queryset = UserProgress.objects.filter(user=request.user)
            mastery_distribution = {}
            for level in range(6):
                count = progress_queryset.filter(mastery_level=level).count()
                mastery_distribution[str(level)] = count
            
            # Difficulty level progress
            difficulty_progress = []
            for difficulty in DifficultyLevel.objects.all().order_by('order'):
                from apps.vocabulary.models import Word
                total_words = Word.objects.filter(difficulty_level=difficulty).count()
                learned_words = progress_queryset.filter(
                    word__difficulty_level=difficulty,
                    mastery_level__gte=3
                ).count()
                
                percentage = (learned_words / total_words * 100) if total_words > 0 else 0
                
                difficulty_progress.append({
                    'level': difficulty.cefr_level,
                    'total': total_words,
                    'learned': learned_words,
                    'percentage': round(percentage, 2)
                })
            
            response_data = {
                'mastery_distribution': mastery_distribution,
                'difficulty_progress': difficulty_progress
            }
            
            return self.success_response(
                data=response_data,
                message="Progress retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Error getting progress: {e}")
            return self.error_response(
                message="Failed to retrieve progress",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='daily')
    def daily_statistics(self, request):
        """
        Get daily statistics for past X days
        
        Query Parameters:
            - days: Number of days (default: 7, max: 90)
        
        Returns:
            {
                "success": true,
                "message": "Daily statistics retrieved successfully",
                "data": [
                    {
                        "date": "2024-11-01",
                        "duration_minutes": 45,
                        "words_reviewed": 15,
                        "accuracy_percentage": 87.5,
                        "words_added": 3
                    }
                ]
            }
        """
        try:
            days = min(int(request.query_params.get('days', 7)), 90)
            start_date = timezone.now().date() - timedelta(days=days)
            
            sessions = UserSession.objects.filter(
                user=request.user,
                session_date__gte=start_date
            ).values('session_date').annotate(
                duration_minutes=Sum('duration_minutes'),
                words_reviewed=Sum('words_reviewed'),
                accuracy_percentage=Avg('accuracy_percentage'),
                words_added=Sum('words_added')
            ).order_by('session_date')
            
            data = []
            for session in sessions:
                data.append({
                    'date': session['session_date'],
                    'duration_minutes': session['duration_minutes'] or 0,
                    'words_reviewed': session['words_reviewed'] or 0,
                    'accuracy_percentage': round(session['accuracy_percentage'] or 0, 2),
                    'words_added': session['words_added'] or 0,
                })
            
            return self.success_response(
                data=data,
                message="Daily statistics retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Error getting daily statistics: {e}")
            return self.error_response(
                message="Failed to retrieve daily statistics",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='weekly')
    def weekly_statistics(self, request):
        """
        Get weekly statistics for past weeks
        
        Query Parameters:
            - weeks: Number of weeks (default: 4, max: 12)
        
        Returns:
            {
                "success": true,
                "message": "Weekly statistics retrieved successfully",
                "data": [
                    {
                        "week": "Week 1",
                        "start_date": "2024-10-05",
                        "end_date": "2024-10-11",
                        "total_duration_minutes": 315,
                        "total_words_reviewed": 105,
                        "average_accuracy_percentage": 86.5,
                        "days_active": 7
                    }
                ]
            }
        """
        try:
            weeks = min(int(request.query_params.get('weeks', 4)), 12)
            today = timezone.now().date()
            
            data = []
            for week_offset in range(weeks):
                week_end = today - timedelta(weeks=week_offset, days=today.weekday())
                week_start = week_end - timedelta(days=6)
                
                sessions = UserSession.objects.filter(
                    user=request.user,
                    session_date__gte=week_start,
                    session_date__lte=week_end
                ).aggregate(
                    duration_minutes=Sum('duration_minutes'),
                    words_reviewed=Sum('words_reviewed'),
                    accuracy_percentage=Avg('accuracy_percentage'),
                    days_active=Count('session_date', distinct=True)
                )
                
                data.append({
                    'week': f'Week {week_offset + 1}',
                    'start_date': week_start,
                    'end_date': week_end,
                    'total_duration_minutes': sessions['duration_minutes'] or 0,
                    'total_words_reviewed': sessions['words_reviewed'] or 0,
                    'average_accuracy_percentage': round(sessions['accuracy_percentage'] or 0, 2),
                    'days_active': sessions['days_active'] or 0,
                })
            
            return self.success_response(
                data=data,
                message="Weekly statistics retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Error getting weekly statistics: {e}")
            return self.error_response(
                message="Failed to retrieve weekly statistics",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='monthly')
    def monthly_statistics(self, request):
        """
        Get monthly statistics
        
        Query Parameters:
            - months: Number of months (default: 6, max: 12)
        
        Returns:
            {
                "success": true,
                "message": "Monthly statistics retrieved successfully",
                "data": [...]
            }
        """
        try:
            months = min(int(request.query_params.get('months', 6)), 12)
            today = timezone.now().date()
            
            data = []
            for month_offset in range(months):
                current_date = today.replace(day=1) - timedelta(days=month_offset * 30)
                month_start = current_date.replace(day=1)
                
                # Calculate month end
                if month_start.month == 12:
                    month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
                
                sessions = UserSession.objects.filter(
                    user=request.user,
                    session_date__gte=month_start,
                    session_date__lte=month_end
                ).aggregate(
                    duration_minutes=Sum('duration_minutes'),
                    words_reviewed=Sum('words_reviewed'),
                    accuracy_percentage=Avg('accuracy_percentage'),
                    days_active=Count('session_date', distinct=True)
                )
                
                data.append({
                    'month': f'{month_start.strftime("%B %Y")}',
                    'start_date': month_start,
                    'end_date': month_end,
                    'total_duration_minutes': sessions['duration_minutes'] or 0,
                    'total_words_reviewed': sessions['words_reviewed'] or 0,
                    'average_accuracy_percentage': round(sessions['accuracy_percentage'] or 0, 2),
                    'days_active': sessions['days_active'] or 0,
                })
            
            return self.success_response(
                data=data,
                message="Monthly statistics retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Error getting monthly statistics: {e}")
            return self.error_response(
                message="Failed to retrieve monthly statistics",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='difficulty')
    def difficulty_statistics(self, request):
        """
        Get statistics broken down by difficulty level
        
        Returns:
            {
                "success": true,
                "message": "Difficulty statistics retrieved successfully",
                "data": [
                    {
                        "level": "A1",
                        "total_words": 500,
                        "words_learned": 250,
                        "words_in_progress": 150,
                        "words_not_started": 100,
                        "average_accuracy": 85.5,
                        "mastery_percentage": 50.0
                    }
                ]
            }
        """
        try:
            data = []
            for difficulty in DifficultyLevel.objects.all().order_by('order'):
                from apps.vocabulary.models import Word
                progress_queryset = UserProgress.objects.filter(
                    user=request.user,
                    word__difficulty_level=difficulty
                )
                
                total_words = Word.objects.filter(difficulty_level=difficulty).count()
                words_learned = progress_queryset.filter(mastery_level__gte=3).count()
                words_in_progress = progress_queryset.filter(mastery_level__in=[1, 2]).count()
                words_not_started = total_words - words_learned - words_in_progress
                
                avg_accuracy = progress_queryset.aggregate(Avg('accuracy_percentage'))
                avg_accuracy_value = avg_accuracy['accuracy_percentage__avg'] or 0
                
                mastery_percentage = (words_learned / total_words * 100) if total_words > 0 else 0
                
                data.append({
                    'level': difficulty.cefr_level,
                    'total_words': total_words,
                    'words_learned': words_learned,
                    'words_in_progress': words_in_progress,
                    'words_not_started': words_not_started,
                    'average_accuracy': round(avg_accuracy_value, 2),
                    'mastery_percentage': round(mastery_percentage, 2),
                })
            
            return self.success_response(
                data=data,
                message="Difficulty statistics retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Error getting difficulty statistics: {e}")
            return self.error_response(
                message="Failed to retrieve difficulty statistics",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='sessions')
    def sessions_history(self, request):
        """
        Get user's study sessions history
        
        Query Parameters:
            - page: Page number (default: 1)
            - page_size: Items per page (default: 10, max: 50)
            - days: Filter sessions from last X days (default: 30)
        
        Returns:
            {
                "success": true,
                "message": "Sessions retrieved successfully",
                "data": {
                    "data": [...],
                    "pagination": {...}
                }
            }
        """
        try:
            page = int(request.query_params.get('page', 1))
            page_size = min(int(request.query_params.get('page_size', 10)), 50)
            days = int(request.query_params.get('days', 30))
            
            start_date = timezone.now().date() - timedelta(days=days)
            
            sessions = UserSession.objects.filter(
                user=request.user,
                session_date__gte=start_date
            ).order_by('-session_date')
            
            from ..common import paginate_response
            from .serializers import UserSessionSerializer
            
            total_count = sessions.count()
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            page_sessions = sessions[start_idx:end_idx]
            serializer = UserSessionSerializer(page_sessions, many=True)
            
            pagination_data = paginate_response(
                data=serializer.data,
                page=page,
                page_size=page_size,
                total_count=total_count
            )
            
            return self.success_response(
                data=pagination_data,
                message="Sessions retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Error getting sessions: {e}")
            return self.error_response(
                message="Failed to retrieve sessions",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='performance')
    def performance_metrics(self, request):
        """
        Get comprehensive performance metrics
        
        Returns:
            {
                "success": true,
                "message": "Performance metrics retrieved successfully",
                "data": {
                    "total_study_time_minutes": 1260,
                    "average_daily_study_time": 45,
                    "total_words_reviewed": 315,
                    "overall_accuracy": 85.5,
                    "consistency_score": 8.5,
                    "learning_velocity": 2.5,
                    "recommendations": [...]
                }
            }
        """
        try:
            user = request.user
            
            # Calculate metrics
            sessions = UserSession.objects.filter(user=user)
            total_study_time = sessions.aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
            total_words_reviewed = sessions.aggregate(Sum('words_reviewed'))['words_reviewed__sum'] or 0
            overall_accuracy = sessions.aggregate(Avg('accuracy_percentage'))['accuracy_percentage__avg'] or 0
            
            # Days active
            days_active = sessions.values('session_date').distinct().count()
            average_daily_study = total_study_time / days_active if days_active > 0 else 0
            
            # Consistency score (0-10)
            total_days_range = (timezone.now().date() - user.created_at.date()).days + 1
            consistency_score = min((days_active / total_days_range * 10), 10) if total_days_range > 0 else 0
            
            # Learning velocity (words per day)
            learning_velocity = total_words_reviewed / total_days_range if total_days_range > 0 else 0
            
            # Recommendations
            recommendations = []
            if average_daily_study < 20:
                recommendations.append("Try to study at least 20 minutes daily for better retention")
            if overall_accuracy < 70:
                recommendations.append("Your accuracy is below 70%. Focus on mastering difficult words")
            if consistency_score < 5:
                recommendations.append("Study more consistently to build a strong learning habit")
            if not recommendations:
                recommendations.append("Great job! Keep up the excellent work!")
            
            response_data = {
                'total_study_time_minutes': total_study_time,
                'average_daily_study_time': round(average_daily_study, 2),
                'total_words_reviewed': total_words_reviewed,
                'overall_accuracy': round(overall_accuracy, 2),
                'consistency_score': round(consistency_score, 1),
                'learning_velocity': round(learning_velocity, 2),
                'recommendations': recommendations,
            }
            
            return self.success_response(
                data=response_data,
                message="Performance metrics retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return self.error_response(
                message="Failed to retrieve performance metrics",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
