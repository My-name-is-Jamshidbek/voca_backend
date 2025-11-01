"""
Progress and Session Tracking Models
"""
from djongo import models
from django.utils import timezone
from django.conf import settings


class UserProgress(models.Model):
    """
    Enhanced user progress tracking with spaced repetition
    """
    STATUS_CHOICES = [
        ('new', 'New'),
        ('learning', 'Learning'),
        ('learned', 'Learned'),
        ('mastered', 'Mastered'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    word = models.ForeignKey('vocabulary.Word', on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    times_reviewed = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    next_review = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Progress'
        verbose_name_plural = 'User Progress'
        unique_together = ['user', 'word']
        indexes = [
            models.Index(fields=['user', 'word']),
            models.Index(fields=['status']),
            models.Index(fields=['next_review']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.word.word} ({self.status})"
    
    @property
    def accuracy_rate(self):
        """Calculate accuracy rate"""
        if self.times_reviewed == 0:
            return 0
        return round((self.times_correct / self.times_reviewed) * 100, 2)
    
    def update_progress(self, is_correct=True):
        """Update progress based on review result"""
        self.times_reviewed += 1
        if is_correct:
            self.times_correct += 1
        
        # Update status based on performance
        if self.times_correct >= 5 and self.accuracy_rate >= 90:
            self.status = 'mastered'
        elif self.times_correct >= 3:
            self.status = 'learned'
        elif self.times_reviewed >= 1:
            self.status = 'learning'
        
        # Calculate next review using spaced repetition
        from datetime import timedelta
        if is_correct:
            # Increase interval for correct answers
            interval_days = min(2 ** (self.times_correct - 1), 30)
        else:
            # Reset interval for incorrect answers
            interval_days = 1
        
        self.next_review = timezone.now() + timedelta(days=interval_days)
        self.last_reviewed = timezone.now()
        self.save()


class UserSession(models.Model):
    """
    Daily learning session tracking
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sessions')
    session_date = models.DateField()
    words_learned = models.IntegerField(default=0)
    words_reviewed = models.IntegerField(default=0)
    total_time_minutes = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        unique_together = ['user', 'session_date']
        ordering = ['-session_date']
    
    def __str__(self):
        return f"{self.user.email} - {self.session_date}"
    
    @classmethod
    def get_or_create_today_session(cls, user):
        """Get or create today's session for user"""
        today = timezone.now().date()
        session, created = cls.objects.get_or_create(
            user=user,
            session_date=today,
            defaults={
                'words_learned': 0,
                'words_reviewed': 0,
                'total_time_minutes': 0,
            }
        )
        return session, created
    
    def add_learning_activity(self, words_learned=0, words_reviewed=0, time_minutes=0):
        """Add learning activity to session"""
        self.words_learned += words_learned
        self.words_reviewed += words_reviewed
        self.total_time_minutes += time_minutes
        self.save()