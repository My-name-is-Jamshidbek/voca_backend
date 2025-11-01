"""
Serializers for Progress App Models
"""
from rest_framework import serializers
from django.utils import timezone

from apps.progress.models import UserProgress, UserSession


class UserProgressSerializer(serializers.ModelSerializer):
    """Serializer for UserProgress model"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    word_text = serializers.CharField(source='word.word', read_only=True)
    word_language = serializers.CharField(source='word.language.name', read_only=True)
    difficulty_level = serializers.CharField(source='word.difficulty_level.level', read_only=True)
    accuracy_percentage = serializers.SerializerMethodField()
    days_since_last_review = serializers.SerializerMethodField()
    is_due_for_review = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'user', 'user_username', 'word', 'word_text',
            'word_language', 'difficulty_level', 'status',
            'times_correct', 'times_reviewed', 'streak_count',
            'last_reviewed', 'next_review', 'ease_factor',
            'interval_days', 'created_at', 'updated_at',
            'accuracy_percentage', 'days_since_last_review', 'is_due_for_review'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'accuracy_percentage',
            'days_since_last_review', 'is_due_for_review'
        ]
    
    def get_accuracy_percentage(self, obj):
        """Calculate accuracy percentage"""
        if obj.times_reviewed == 0:
            return None
        return round((obj.times_correct / obj.times_reviewed) * 100, 2)
    
    def get_days_since_last_review(self, obj):
        """Calculate days since last review"""
        if not obj.last_reviewed:
            return None
        return (timezone.now().date() - obj.last_reviewed.date()).days
    
    def get_is_due_for_review(self, obj):
        """Check if word is due for review"""
        if not obj.next_review:
            return False
        return timezone.now() >= obj.next_review


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for UserSession model"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    session_duration = serializers.SerializerMethodField()
    words_per_minute = serializers.SerializerMethodField()
    review_accuracy = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'user', 'user_username', 'session_date',
            'words_learned', 'words_reviewed', 'correct_answers',
            'total_time_minutes', 'session_type', 'created_at', 'updated_at',
            'session_duration', 'words_per_minute', 'review_accuracy'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'session_duration',
            'words_per_minute', 'review_accuracy'
        ]
    
    def get_session_duration(self, obj):
        """Get session duration in human readable format"""
        if obj.total_time_minutes < 60:
            return f"{obj.total_time_minutes} minutes"
        hours = obj.total_time_minutes // 60
        minutes = obj.total_time_minutes % 60
        return f"{hours}h {minutes}m"
    
    def get_words_per_minute(self, obj):
        """Calculate words per minute rate"""
        if obj.total_time_minutes == 0:
            return 0
        total_words = obj.words_learned + obj.words_reviewed
        return round(total_words / obj.total_time_minutes, 2)
    
    def get_review_accuracy(self, obj):
        """Calculate review accuracy percentage"""
        if obj.words_reviewed == 0:
            return None
        return round((obj.correct_answers / obj.words_reviewed) * 100, 2)