import secrets
import string
from datetime import datetime, timedelta
from djongo import models
from apps.accounts.models import User
from apps.versioning.models import AppVersion


class MobileAppToken(models.Model):
    """
    Token for mobile applications with version and role-based permissions
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('revoked', 'Revoked'),
    ]
    
    # Basic fields
    token = models.CharField(max_length=64, unique=True, editable=False)
    name = models.CharField(max_length=100, help_text="Token name for identification")
    description = models.TextField(blank=True, help_text="Token description")
    
    # Mobile app specific fields
    app_version = models.ForeignKey(
        AppVersion, 
        on_delete=models.CASCADE,
        help_text="Required mobile app version"
    )
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES,
        help_text="Role permissions for this token"
    )
    
    # Status and tracking
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_mobile_tokens')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    max_usage_count = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum usage count (optional)")
    
    # IP restrictions
    allowed_ips = models.JSONField(default=list, blank=True, help_text="List of allowed IP addresses")
    
    class Meta:
        db_table = 'mobile_app_tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['status']),
            models.Index(fields=['role']),
            models.Index(fields=['app_version']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.role}) - {self.app_version}"
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        super().save(*args, **kwargs)
    
    def generate_token(self):
        """Generate a secure random token"""
        alphabet = string.ascii_letters + string.digits
        return 'mob_' + ''.join(secrets.choice(alphabet) for _ in range(60))
    
    def is_valid(self):
        """Check if token is valid and not expired"""
        if self.status != 'active':
            return False
        
        if self.expires_at and self.expires_at <= datetime.now():
            return False
        
        if self.max_usage_count and self.usage_count >= self.max_usage_count:
            return False
        
        return True
    
    def increment_usage(self):
        """Increment usage count and update last used timestamp"""
        self.usage_count += 1
        self.last_used_at = datetime.now()
        self.save(update_fields=['usage_count', 'last_used_at'])


class CRUDSPermission(models.Model):
    """
    CRUD permissions for specific models
    """
    model_name = models.CharField(max_length=50, help_text="Model name (e.g., 'Word', 'User')")
    can_create = models.BooleanField(default=False)
    can_read = models.BooleanField(default=True)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_list = models.BooleanField(default=True)
    
    class Meta:
        abstract = True


class APIClientToken(models.Model):
    """
    Token for API clients with detailed CRUD permissions for each model
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('revoked', 'Revoked'),
    ]
    
    # Basic fields
    token = models.CharField(max_length=64, unique=True, editable=False)
    name = models.CharField(max_length=100, help_text="Token name for identification")
    description = models.TextField(blank=True, help_text="Token description")
    
    # Client information
    client_name = models.CharField(max_length=100, help_text="API client name")
    client_email = models.EmailField(help_text="Client contact email")
    client_organization = models.CharField(max_length=100, blank=True, help_text="Client organization")
    
    # Status and tracking
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_api_tokens')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    max_usage_count = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum usage count (optional)")
    
    # Rate limiting
    rate_limit_per_hour = models.PositiveIntegerField(default=1000, help_text="Requests per hour limit")
    rate_limit_per_day = models.PositiveIntegerField(default=10000, help_text="Requests per day limit")
    
    # IP restrictions
    allowed_ips = models.JSONField(default=list, blank=True, help_text="List of allowed IP addresses")
    
    # Scope restrictions
    allowed_endpoints = models.JSONField(default=list, blank=True, help_text="List of allowed API endpoints")
    
    class Meta:
        db_table = 'api_client_tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['status']),
            models.Index(fields=['client_name']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.client_name}"
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        super().save(*args, **kwargs)
    
    def generate_token(self):
        """Generate a secure random token"""
        alphabet = string.ascii_letters + string.digits
        return 'api_' + ''.join(secrets.choice(alphabet) for _ in range(60))
    
    def is_valid(self):
        """Check if token is valid and not expired"""
        if self.status != 'active':
            return False
        
        if self.expires_at and self.expires_at <= datetime.now():
            return False
        
        if self.max_usage_count and self.usage_count >= self.max_usage_count:
            return False
        
        return True
    
    def increment_usage(self):
        """Increment usage count and update last used timestamp"""
        self.usage_count += 1
        self.last_used_at = datetime.now()
        self.save(update_fields=['usage_count', 'last_used_at'])


class TokenModelPermission(models.Model):
    """
    CRUD permissions for specific models associated with API client tokens
    """
    MODEL_CHOICES = [
        # accounts app
        ('User', 'User'),
        ('UserDevice', 'UserDevice'),
        
        # vocabulary app
        ('Language', 'Language'),
        ('Book', 'Book'),
        ('Chapter', 'Chapter'),
        ('DifficultyLevel', 'DifficultyLevel'),
        ('Word', 'Word'),
        ('WordTranslation', 'WordTranslation'),
        ('WordDefinition', 'WordDefinition'),
        ('Collection', 'Collection'),
        ('CollectionWord', 'CollectionWord'),
        
        # progress app
        ('UserProgress', 'UserProgress'),
        ('UserSession', 'UserSession'),
        
        # versioning app
        ('AppVersion', 'AppVersion'),
        
        # tokens app
        ('MobileAppToken', 'MobileAppToken'),
        ('APIClientToken', 'APIClientToken'),
        ('TokenModelPermission', 'TokenModelPermission'),
    ]
    
    token = models.ForeignKey(
        APIClientToken, 
        on_delete=models.CASCADE, 
        related_name='model_permissions'
    )
    model_name = models.CharField(max_length=50, choices=MODEL_CHOICES)
    
    # CRUD permissions
    can_create = models.BooleanField(default=False, help_text="Can create new records")
    can_read = models.BooleanField(default=True, help_text="Can read/retrieve records")
    can_update = models.BooleanField(default=False, help_text="Can update existing records")
    can_delete = models.BooleanField(default=False, help_text="Can delete records")
    can_list = models.BooleanField(default=True, help_text="Can list/search records")
    
    # Additional permissions
    can_bulk_create = models.BooleanField(default=False, help_text="Can bulk create records")
    can_bulk_update = models.BooleanField(default=False, help_text="Can bulk update records")
    can_bulk_delete = models.BooleanField(default=False, help_text="Can bulk delete records")
    
    # Field-level restrictions
    restricted_fields = models.JSONField(
        default=list, 
        blank=True, 
        help_text="List of fields that are restricted for this token"
    )
    readonly_fields = models.JSONField(
        default=list, 
        blank=True, 
        help_text="List of fields that are read-only for this token"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'token_model_permissions'
        unique_together = ['token', 'model_name']
        ordering = ['model_name']
    
    def __str__(self):
        perms = []
        if self.can_create: perms.append('C')
        if self.can_read: perms.append('R')
        if self.can_update: perms.append('U')
        if self.can_delete: perms.append('D')
        if self.can_list: perms.append('L')
        
        return f"{self.token.name} - {self.model_name} ({''.join(perms)})"
    
    def get_permissions_summary(self):
        """Get a summary of permissions for this model"""
        return {
            'create': self.can_create,
            'read': self.can_read,
            'update': self.can_update,
            'delete': self.can_delete,
            'list': self.can_list,
            'bulk_create': self.can_bulk_create,
            'bulk_update': self.can_bulk_update,
            'bulk_delete': self.can_bulk_delete,
            'restricted_fields': self.restricted_fields,
            'readonly_fields': self.readonly_fields,
        }


class TokenUsageLog(models.Model):
    """
    Log of token usage for monitoring and analytics
    """
    TOKEN_TYPE_CHOICES = [
        ('mobile', 'Mobile App Token'),
        ('api', 'API Client Token'),
    ]
    
    # Token information
    token_type = models.CharField(max_length=10, choices=TOKEN_TYPE_CHOICES)
    token_id = models.CharField(max_length=24)  # ObjectId as string
    token_name = models.CharField(max_length=100)
    
    # Request information
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)  # GET, POST, PUT, DELETE, etc.
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Response information
    status_code = models.PositiveIntegerField()
    response_time_ms = models.PositiveIntegerField(help_text="Response time in milliseconds")
    
    # Additional data
    request_data_size = models.PositiveIntegerField(default=0, help_text="Request size in bytes")
    response_data_size = models.PositiveIntegerField(default=0, help_text="Response size in bytes")
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'token_usage_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['token_type', 'token_id']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['endpoint']),
            models.Index(fields=['status_code']),
        ]
    
    def __str__(self):
        return f"{self.token_name} - {self.method} {self.endpoint} ({self.status_code})"
