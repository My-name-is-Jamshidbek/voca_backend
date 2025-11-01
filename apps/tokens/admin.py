from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import MobileAppToken, APIClientToken, TokenModelPermission, TokenUsageLog


class TokenModelPermissionInline(admin.TabularInline):
    model = TokenModelPermission
    extra = 0
    fields = [
        'model_name', 'can_create', 'can_read', 'can_update', 
        'can_delete', 'can_list', 'can_bulk_create', 'can_bulk_update', 
        'can_bulk_delete', 'restricted_fields', 'readonly_fields'
    ]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MobileAppToken)
class MobileAppTokenAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'role', 'app_version', 'status', 'usage_count', 
        'created_by', 'created_at', 'last_used_at', 'expires_at'
    ]
    list_filter = ['role', 'status', 'app_version', 'created_at', 'expires_at']
    search_fields = ['name', 'description', 'token', 'created_by__username']
    readonly_fields = [
        'token', 'created_at', 'updated_at', 'last_used_at', 
        'usage_count', 'token_display'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'token_display')
        }),
        ('Mobile App Configuration', {
            'fields': ('app_version', 'role')
        }),
        ('Status & Security', {
            'fields': ('status', 'expires_at', 'allowed_ips')
        }),
        ('Usage Limits', {
            'fields': ('max_usage_count', 'usage_count')
        }),
        ('Tracking', {
            'fields': ('created_by', 'created_at', 'updated_at', 'last_used_at'),
            'classes': ('collapse',)
        }),
    )
    
    def token_display(self, obj):
        if obj.token:
            return format_html(
                '<code style="background: #f1f1f1; padding: 4px; border-radius: 3px;">{}</code>',
                obj.token
            )
        return '-'
    token_display.short_description = 'Token'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(APIClientToken)
class APIClientTokenAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'client_name', 'client_email', 'status', 'usage_count',
        'rate_limit_per_hour', 'created_at', 'last_used_at', 'expires_at'
    ]
    list_filter = ['status', 'created_at', 'expires_at', 'client_organization']
    search_fields = [
        'name', 'description', 'token', 'client_name', 
        'client_email', 'client_organization'
    ]
    readonly_fields = [
        'token', 'created_at', 'updated_at', 'last_used_at', 
        'usage_count', 'token_display', 'permissions_summary'
    ]
    inlines = [TokenModelPermissionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'token_display')
        }),
        ('Client Information', {
            'fields': ('client_name', 'client_email', 'client_organization')
        }),
        ('Status & Security', {
            'fields': ('status', 'expires_at', 'allowed_ips', 'allowed_endpoints')
        }),
        ('Rate Limiting', {
            'fields': ('rate_limit_per_hour', 'rate_limit_per_day', 'max_usage_count', 'usage_count')
        }),
        ('Permissions Summary', {
            'fields': ('permissions_summary',),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('created_by', 'created_at', 'updated_at', 'last_used_at'),
            'classes': ('collapse',)
        }),
    )
    
    def token_display(self, obj):
        if obj.token:
            return format_html(
                '<code style="background: #f1f1f1; padding: 4px; border-radius: 3px;">{}</code>',
                obj.token
            )
        return '-'
    token_display.short_description = 'Token'
    
    def permissions_summary(self, obj):
        if obj.pk:
            permissions = obj.model_permissions.all()
            if permissions:
                html = '<div style="max-height: 200px; overflow-y: auto;">'
                for perm in permissions:
                    perms = []
                    if perm.can_create: perms.append('C')
                    if perm.can_read: perms.append('R')
                    if perm.can_update: perms.append('U')
                    if perm.can_delete: perms.append('D')
                    if perm.can_list: perms.append('L')
                    
                    html += f'<div><strong>{perm.model_name}:</strong> {"".join(perms) or "No permissions"}</div>'
                html += '</div>'
                return mark_safe(html)
        return 'No permissions set'
    permissions_summary.short_description = 'Model Permissions'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TokenModelPermission)
class TokenModelPermissionAdmin(admin.ModelAdmin):
    list_display = [
        'token', 'model_name', 'permissions_display', 
        'created_at', 'updated_at'
    ]
    list_filter = [
        'model_name', 'can_create', 'can_read', 'can_update', 
        'can_delete', 'can_list', 'created_at'
    ]
    search_fields = ['token__name', 'model_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('token', 'model_name')
        }),
        ('CRUD Permissions', {
            'fields': ('can_create', 'can_read', 'can_update', 'can_delete', 'can_list')
        }),
        ('Bulk Operations', {
            'fields': ('can_bulk_create', 'can_bulk_update', 'can_bulk_delete')
        }),
        ('Field Restrictions', {
            'fields': ('restricted_fields', 'readonly_fields'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def permissions_display(self, obj):
        perms = []
        if obj.can_create: perms.append('C')
        if obj.can_read: perms.append('R')
        if obj.can_update: perms.append('U')
        if obj.can_delete: perms.append('D')
        if obj.can_list: perms.append('L')
        
        bulk_perms = []
        if obj.can_bulk_create: bulk_perms.append('BC')
        if obj.can_bulk_update: bulk_perms.append('BU')
        if obj.can_bulk_delete: bulk_perms.append('BD')
        
        result = ''.join(perms) or 'No permissions'
        if bulk_perms:
            result += f' + {"".join(bulk_perms)}'
        
        return result
    permissions_display.short_description = 'Permissions'


@admin.register(TokenUsageLog)
class TokenUsageLogAdmin(admin.ModelAdmin):
    list_display = [
        'token_name', 'token_type', 'method', 'endpoint', 
        'status_code', 'response_time_ms', 'ip_address', 'timestamp'
    ]
    list_filter = [
        'token_type', 'method', 'status_code', 'timestamp',
        'endpoint'
    ]
    search_fields = [
        'token_name', 'endpoint', 'ip_address', 'user_agent'
    ]
    readonly_fields = [
        'token_type', 'token_id', 'token_name', 'endpoint', 'method',
        'ip_address', 'user_agent', 'status_code', 'response_time_ms',
        'request_data_size', 'response_data_size', 'timestamp'
    ]
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Token Information', {
            'fields': ('token_type', 'token_id', 'token_name')
        }),
        ('Request Details', {
            'fields': ('method', 'endpoint', 'ip_address', 'user_agent')
        }),
        ('Response Details', {
            'fields': ('status_code', 'response_time_ms')
        }),
        ('Data Size', {
            'fields': ('request_data_size', 'response_data_size'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent manual creation of usage logs
        return False
    
    def has_change_permission(self, request, obj=None):
        # Make usage logs read-only
        return False
