"""
App Version Management Models
"""
from djongo import models
from django.utils import timezone


class AppVersion(models.Model):
    """
    App version management for mobile sync and compatibility
    """
    PLATFORM_CHOICES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
        ('desktop', 'Desktop'),
    ]
    
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    version_number = models.CharField(max_length=20)  # e.g., "1.2.3"
    build_number = models.IntegerField(null=True, blank=True)
    release_notes = models.TextField(blank=True, null=True)
    is_mandatory = models.BooleanField(default=False)
    min_supported_version = models.CharField(max_length=20, blank=True, null=True)
    released_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'App Version'
        verbose_name_plural = 'App Versions'
        ordering = ['-created_at']
        unique_together = ['platform', 'version_number']
    
    def __str__(self):
        return f"{self.platform} v{self.version_number}"
    
    @classmethod
    def get_latest_version(cls, platform):
        """Get the latest version for a platform"""
        return cls.objects.filter(platform=platform).first()
    
    @classmethod
    def is_version_supported(cls, platform, version):
        """Check if a version is still supported"""
        latest = cls.get_latest_version(platform)
        if not latest or not latest.min_supported_version:
            return True
        
        # Simple version comparison (assumes semantic versioning)
        def version_tuple(v):
            return tuple(map(int, (v.split("."))))
        
        try:
            return version_tuple(version) >= version_tuple(latest.min_supported_version)
        except (ValueError, AttributeError):
            return True  # If version parsing fails, assume supported
    
    def is_update_required(self, current_version):
        """Check if update is required for current version"""
        if self.is_mandatory:
            return True
        return False