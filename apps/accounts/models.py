"""
User Models for Authentication and User Management
"""
from django.contrib.auth.models import AbstractUser
from djongo import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model based on database diagram
    """
    AUTH_PROVIDER_CHOICES = [
        ('google', 'Google'),
        ('apple', 'Apple'),
        ('email', 'Email'),
    ]
    
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    auth_provider = models.CharField(max_length=50, choices=AUTH_PROVIDER_CHOICES, default='email')
    auth_provider_id = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    profile_picture = models.TextField(blank=True, null=True)  # URL or base64
    preferred_language = models.CharField(max_length=10, default='en')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """Return the full name of the user"""
        return f"{self.first_name} {self.last_name}".strip() or self.username or self.email


class UserDevice(models.Model):
    """
    User device management for sync across platforms
    """
    PLATFORM_CHOICES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
        ('desktop', 'Desktop'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    app_version = models.CharField(max_length=20, blank=True, null=True)
    device_model = models.CharField(max_length=100, blank=True, null=True)
    os_version = models.CharField(max_length=50, blank=True, null=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Device'
        verbose_name_plural = 'User Devices'
        ordering = ['-last_sync']
        indexes = [
            models.Index(fields=['user', 'platform']),
            models.Index(fields=['device_id']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.platform} ({self.device_model})"