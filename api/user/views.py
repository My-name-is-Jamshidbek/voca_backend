"""
User APIs - Endpoints accessible to regular users
Includes vocabulary learning, progress tracking, and profile management
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta

from apps.accounts.models import User, UserDevice
from apps.vocabulary.models import Language, Word, Collection, CollectionWord
from apps.progress.models import UserProgress, UserSession
from apps.versioning.models import AppVersion
from api.base.permissions import UserRolePermission, IsOwnerOrReadOnly
from api.base.responses import success_response, error_response, ResponseMixin
import logging

logger = logging.getLogger(__name__)


class UserDashboardView(APIView, ResponseMixin):
    """
    User dashboard with overview statistics and recent activity
    """
    permission_classes = [IsAuthenticated, UserRolePermission]
    
    def get(self, request):
        """Get user dashboard data"""
        user = request.user
        
        # Get basic user statistics
        total_words_learned = UserProgress.objects.filter(user=user).count()
        words_mastered = UserProgress.objects.filter(
            user=user, 
            mastery_level__gte=4
        ).count()
        
        # Recent session activity (last 7 days)
        last_week = timezone.now() - timedelta(days=7)
        recent_sessions = UserSession.objects.filter(
            user=user,
            start_time__gte=last_week
        ).order_by('-start_time')[:5]
        
        # Learning streak
        learning_streak = self.calculate_learning_streak(user)
        
        # Collection progress
        user_collections = Collection.objects.filter(
            collectionword__user_progress__user=user
        ).distinct().annotate(
            total_words=Count('collectionword'),
            learned_words=Count(
                'collectionword__user_progress',
                filter=Q(collectionword__user_progress__user=user)
            )
        )
        
        collections_data = [
            {
                'id': str(collection.id),
                'name': collection.name,
                'description': collection.description,
                'total_words': collection.total_words,
                'learned_words': collection.learned_words,
                'progress_percentage': round(
                    (collection.learned_words / collection.total_words) * 100, 1
                ) if collection.total_words > 0 else 0,
            }
            for collection in user_collections[:5]
        ]
        
        # Recent session data
        sessions_data = [
            {
                'id': str(session.id),
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'duration_minutes': session.duration_minutes,
                'words_practiced': session.words_practiced,
                'correct_answers': session.correct_answers,
                'accuracy_percentage': session.accuracy_percentage,
            }
            for session in recent_sessions
        ]
        
        dashboard_data = {
            'user_stats': {
                'total_words_learned': total_words_learned,
                'words_mastered': words_mastered,
                'learning_streak_days': learning_streak,
                'mastery_percentage': round(
                    (words_mastered / total_words_learned) * 100, 1
                ) if total_words_learned > 0 else 0,
            },
            'recent_collections': collections_data,
            'recent_sessions': sessions_data,
            'weekly_goal_progress': self.get_weekly_goal_progress(user),
        }
        
        return self.success_response(
            data=dashboard_data,
            message="Dashboard data retrieved successfully"
        )
    
    def calculate_learning_streak(self, user):
        """Calculate user's current learning streak in days"""
        sessions = UserSession.objects.filter(user=user).order_by('-start_time')
        
        if not sessions:
            return 0
        
        streak_days = 0
        current_date = timezone.now().date()
        
        # Check if user practiced today or yesterday
        last_session_date = sessions.first().start_time.date()
        if last_session_date == current_date:
            streak_days = 1
            current_date = current_date - timedelta(days=1)
        elif last_session_date == current_date - timedelta(days=1):
            streak_days = 1
            current_date = last_session_date - timedelta(days=1)
        else:
            return 0
        
        # Count consecutive days with sessions
        for session in sessions[1:]:
            session_date = session.start_time.date()
            if session_date == current_date:
                streak_days += 1
                current_date = current_date - timedelta(days=1)
            else:
                break
        
        return streak_days
    
    def get_weekly_goal_progress(self, user):
        """Get progress towards weekly learning goal"""
        week_start = timezone.now().date() - timedelta(days=timezone.now().weekday())
        week_sessions = UserSession.objects.filter(
            user=user,
            start_time__date__gte=week_start
        )
        
        total_minutes = sum(session.duration_minutes or 0 for session in week_sessions)
        weekly_goal = 210  # 30 minutes per day * 7 days
        
        return {
            'minutes_practiced': total_minutes,
            'goal_minutes': weekly_goal,
            'progress_percentage': round((total_minutes / weekly_goal) * 100, 1),
            'sessions_this_week': week_sessions.count(),
        }


class UserVocabularyView(APIView, ResponseMixin):
    """
    User vocabulary management - words they're learning
    """
    permission_classes = [IsAuthenticated, UserRolePermission]
    
    def get(self, request):
        """Get user's vocabulary with progress"""
        user = request.user
        
        # Query parameters
        difficulty = request.query_params.get('difficulty')
        language_id = request.query_params.get('language')
        mastery_level = request.query_params.get('mastery_level')
        search = request.query_params.get('search')
        
        # Get user's word progress
        progress_query = UserProgress.objects.filter(user=user).select_related(
            'word', 'word__language', 'word__difficulty_level'
        )
        
        # Apply filters
        if difficulty:
            progress_query = progress_query.filter(word__difficulty_level__level=difficulty)
        
        if language_id:
            progress_query = progress_query.filter(word__language_id=language_id)
        
        if mastery_level:
            progress_query = progress_query.filter(mastery_level=mastery_level)
        
        if search:
            progress_query = progress_query.filter(
                Q(word__word__icontains=search) |
                Q(word__wordtranslation__translation__icontains=search) |
                Q(word__worddefinition__definition__icontains=search)
            )
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = progress_query.count()
        progress_items = progress_query[start:end]
        
        # Format response data
        vocabulary_data = []
        for progress in progress_items:
            word = progress.word
            
            # Get translations and definitions
            translations = [
                {
                    'language': trans.language.name,
                    'translation': trans.translation,
                    'language_code': trans.language.code,
                }
                for trans in word.wordtranslation_set.all()
            ]
            
            definitions = [
                {
                    'definition': defn.definition,
                    'example': defn.example_sentence,
                }
                for defn in word.worddefinition_set.all()
            ]
            
            vocabulary_data.append({
                'progress_id': str(progress.id),
                'word': {
                    'id': str(word.id),
                    'word': word.word,
                    'language': word.language.name,
                    'language_code': word.language.code,
                    'difficulty_level': word.difficulty_level.level,
                    'pronunciation': word.pronunciation,
                    'translations': translations,
                    'definitions': definitions,
                },
                'progress': {
                    'mastery_level': progress.mastery_level,
                    'review_count': progress.review_count,
                    'correct_count': progress.correct_count,
                    'last_reviewed': progress.last_reviewed.isoformat() if progress.last_reviewed else None,
                    'next_review': progress.next_review.isoformat() if progress.next_review else None,
                    'ease_factor': float(progress.ease_factor),
                    'interval_days': progress.interval_days,
                },
            })
        
        response_data = {
            'vocabulary': vocabulary_data,
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
            message="Vocabulary retrieved successfully"
        )


class UserCollectionsView(APIView, ResponseMixin):
    """
    User collections management
    """
    permission_classes = [IsAuthenticated, UserRolePermission]
    
    def get(self, request):
        """Get user's collections with progress"""
        user = request.user
        
        # Get collections that user has words from
        collections = Collection.objects.filter(
            collectionword__user_progress__user=user
        ).distinct().annotate(
            total_words=Count('collectionword'),
            learned_words=Count(
                'collectionword__user_progress',
                filter=Q(collectionword__user_progress__user=user)
            ),
            avg_mastery=Avg(
                'collectionword__user_progress__mastery_level',
                filter=Q(collectionword__user_progress__user=user)
            )
        )
        
        collections_data = []
        for collection in collections:
            progress_percentage = round(
                (collection.learned_words / collection.total_words) * 100, 1
            ) if collection.total_words > 0 else 0
            
            collections_data.append({
                'id': str(collection.id),
                'name': collection.name,
                'description': collection.description,
                'category': collection.category,
                'difficulty_level': collection.difficulty_level.level if collection.difficulty_level else None,
                'total_words': collection.total_words,
                'learned_words': collection.learned_words,
                'progress_percentage': progress_percentage,
                'average_mastery': round(collection.avg_mastery or 0, 1),
                'created_at': collection.created_at.isoformat(),
            })
        
        return self.success_response(
            data={'collections': collections_data},
            message="Collections retrieved successfully"
        )


class UserProgressView(APIView, ResponseMixin):
    """
    User learning progress and statistics
    """
    permission_classes = [IsAuthenticated, UserRolePermission]
    
    def get(self, request):
        """Get detailed user progress statistics"""
        user = request.user
        
        # Time range filter
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Learning sessions in time range
        sessions = UserSession.objects.filter(
            user=user,
            start_time__gte=start_date
        ).order_by('start_time')
        
        # Daily statistics
        daily_stats = {}
        for session in sessions:
            date_key = session.start_time.date().isoformat()
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    'date': date_key,
                    'sessions': 0,
                    'total_minutes': 0,
                    'words_practiced': 0,
                    'correct_answers': 0,
                    'total_answers': 0,
                }
            
            daily_stats[date_key]['sessions'] += 1
            daily_stats[date_key]['total_minutes'] += session.duration_minutes or 0
            daily_stats[date_key]['words_practiced'] += session.words_practiced or 0
            daily_stats[date_key]['correct_answers'] += session.correct_answers or 0
            daily_stats[date_key]['total_answers'] += session.total_answers or 0
        
        # Calculate accuracy for each day
        for stats in daily_stats.values():
            if stats['total_answers'] > 0:
                stats['accuracy_percentage'] = round(
                    (stats['correct_answers'] / stats['total_answers']) * 100, 1
                )
            else:
                stats['accuracy_percentage'] = 0
        
        # Overall statistics
        total_sessions = sessions.count()
        total_minutes = sum(session.duration_minutes or 0 for session in sessions)
        total_words = sum(session.words_practiced or 0 for session in sessions)
        total_correct = sum(session.correct_answers or 0 for session in sessions)
        total_answers = sum(session.total_answers or 0 for session in sessions)
        
        overall_accuracy = round(
            (total_correct / total_answers) * 100, 1
        ) if total_answers > 0 else 0
        
        # Mastery level distribution
        mastery_distribution = UserProgress.objects.filter(user=user).values(
            'mastery_level'
        ).annotate(count=Count('id'))
        
        mastery_data = {level: 0 for level in range(6)}  # 0-5 mastery levels
        for item in mastery_distribution:
            mastery_data[item['mastery_level']] = item['count']
        
        progress_data = {
            'time_range_days': days,
            'overall_stats': {
                'total_sessions': total_sessions,
                'total_minutes': total_minutes,
                'total_words_practiced': total_words,
                'overall_accuracy': overall_accuracy,
                'average_session_length': round(total_minutes / total_sessions, 1) if total_sessions > 0 else 0,
            },
            'daily_progress': list(daily_stats.values()),
            'mastery_distribution': [
                {'level': level, 'count': count, 'label': self.get_mastery_label(level)}
                for level, count in mastery_data.items()
            ],
        }
        
        return self.success_response(
            data=progress_data,
            message="Progress statistics retrieved successfully"
        )
    
    def get_mastery_label(self, level):
        """Get human-readable mastery level label"""
        labels = {
            0: 'Not Started',
            1: 'Beginner',
            2: 'Learning',
            3: 'Practicing',
            4: 'Advanced',
            5: 'Mastered'
        }
        return labels.get(level, 'Unknown')


class UserReviewView(APIView, ResponseMixin):
    """
    Spaced repetition review system for users
    """
    permission_classes = [IsAuthenticated, UserRolePermission]
    
    def get(self, request):
        """Get words due for review"""
        user = request.user
        now = timezone.now()
        
        # Get words due for review
        due_reviews = UserProgress.objects.filter(
            user=user,
            next_review__lte=now
        ).select_related('word', 'word__language').order_by('next_review')
        
        # Limit to reasonable number for one session
        limit = int(request.query_params.get('limit', 20))
        due_reviews = due_reviews[:limit]
        
        review_words = []
        for progress in due_reviews:
            word = progress.word
            
            # Get translations for the user's preferred language
            translations = word.wordtranslation_set.filter(
                language__code=user.preferred_language
            )
            if not translations:
                # Fallback to English if preferred language not available
                translations = word.wordtranslation_set.filter(language__code='en')
            
            review_words.append({
                'progress_id': str(progress.id),
                'word': {
                    'id': str(word.id),
                    'word': word.word,
                    'language': word.language.name,
                    'pronunciation': word.pronunciation,
                    'translations': [
                        {
                            'language': trans.language.name,
                            'translation': trans.translation,
                        }
                        for trans in translations
                    ],
                },
                'review_info': {
                    'mastery_level': progress.mastery_level,
                    'review_count': progress.review_count,
                    'last_reviewed': progress.last_reviewed.isoformat() if progress.last_reviewed else None,
                    'days_overdue': (now.date() - progress.next_review.date()).days if progress.next_review else 0,
                }
            })
        
        return self.success_response(
            data={
                'review_words': review_words,
                'total_due': len(review_words),
            },
            message="Review words retrieved successfully"
        )
    
    def post(self, request):
        """Submit review results"""
        user = request.user
        review_results = request.data.get('results', [])
        
        if not review_results:
            return self.error_response(
                message="Review results are required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Process each review result
        updated_progress = []
        for result in review_results:
            progress_id = result.get('progress_id')
            is_correct = result.get('is_correct', False)
            
            try:
                progress = UserProgress.objects.get(id=progress_id, user=user)
                
                # Update progress based on spaced repetition algorithm
                progress.review_count += 1
                if is_correct:
                    progress.correct_count += 1
                
                # Update mastery level and next review date
                self.update_spaced_repetition(progress, is_correct)
                progress.last_reviewed = timezone.now()
                progress.save()
                
                updated_progress.append({
                    'progress_id': str(progress.id),
                    'new_mastery_level': progress.mastery_level,
                    'next_review': progress.next_review.isoformat() if progress.next_review else None,
                })
                
            except UserProgress.DoesNotExist:
                logger.warning(f"Progress {progress_id} not found for user {user.id}")
                continue
        
        return self.success_response(
            data={'updated_progress': updated_progress},
            message="Review results submitted successfully"
        )
    
    def update_spaced_repetition(self, progress, is_correct):
        """Update progress using spaced repetition algorithm"""
        if is_correct:
            # Increase interval and mastery level
            progress.interval_days = max(1, int(progress.interval_days * progress.ease_factor))
            if progress.mastery_level < 5:
                progress.mastery_level += 1
            
            # Adjust ease factor
            if progress.ease_factor < 2.5:
                progress.ease_factor += 0.1
        else:
            # Reset interval and potentially decrease mastery level
            progress.interval_days = 1
            if progress.mastery_level > 0:
                progress.mastery_level -= 1
            
            # Adjust ease factor
            if progress.ease_factor > 1.3:
                progress.ease_factor -= 0.2
        
        # Calculate next review date
        progress.next_review = timezone.now() + timedelta(days=progress.interval_days)


class UserProfileDetailView(APIView, ResponseMixin):
    """
    Enhanced user profile with learning preferences and statistics
    """
    permission_classes = [IsAuthenticated, UserRolePermission]
    
    def get(self, request):
        """Get comprehensive user profile"""
        user = request.user
        
        # Learning statistics
        total_words = UserProgress.objects.filter(user=user).count()
        mastered_words = UserProgress.objects.filter(user=user, mastery_level=5).count()
        total_sessions = UserSession.objects.filter(user=user).count()
        total_study_time = UserSession.objects.filter(user=user).aggregate(
            total_minutes=Sum('duration_minutes')
        )['total_minutes'] or 0
        
        # Learning languages
        learning_languages = Language.objects.filter(
            word__user_progress__user=user
        ).distinct().values('id', 'name', 'code')
        
        profile_data = {
            'user_info': {
                'id': str(user.id),
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.full_name,
                'preferred_language': user.preferred_language,
                'profile_picture': user.profile_picture,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
            },
            'learning_stats': {
                'total_words_learned': total_words,
                'words_mastered': mastered_words,
                'total_sessions': total_sessions,
                'total_study_time_minutes': total_study_time,
                'mastery_percentage': round((mastered_words / total_words) * 100, 1) if total_words > 0 else 0,
            },
            'learning_languages': list(learning_languages),
            'preferences': {
                'preferred_language': user.preferred_language,
                'daily_goal_minutes': 30,  # Could be stored in user profile
                'notification_enabled': True,  # Could be stored in user profile
            }
        }
        
        return self.success_response(
            data=profile_data,
            message="User profile retrieved successfully"
        )