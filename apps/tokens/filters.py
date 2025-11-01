import django_filters
from django.db import models
from .models import MobileAppToken, APIClientToken, TokenUsageLog


class MobileAppTokenFilter(django_filters.FilterSet):
    """
    Filter for Mobile App Tokens
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    role = django_filters.ChoiceFilter(choices=MobileAppToken.ROLE_CHOICES)
    status = django_filters.ChoiceFilter(choices=MobileAppToken.STATUS_CHOICES)
    app_version = django_filters.CharFilter(field_name='app_version__version_name', lookup_expr='icontains')
    created_by = django_filters.CharFilter(field_name='created_by__username', lookup_expr='icontains')
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    expires_after = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='gte')
    expires_before = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='lte')
    last_used_after = django_filters.DateTimeFilter(field_name='last_used_at', lookup_expr='gte')
    last_used_before = django_filters.DateTimeFilter(field_name='last_used_at', lookup_expr='lte')
    
    # Usage filters
    usage_count_min = django_filters.NumberFilter(field_name='usage_count', lookup_expr='gte')
    usage_count_max = django_filters.NumberFilter(field_name='usage_count', lookup_expr='lte')
    
    # Boolean filters
    is_expired = django_filters.BooleanFilter(method='filter_expired')
    has_expiry = django_filters.BooleanFilter(field_name='expires_at', lookup_expr='isnull', exclude=True)
    has_usage_limit = django_filters.BooleanFilter(field_name='max_usage_count', lookup_expr='isnull', exclude=True)
    
    class Meta:
        model = MobileAppToken
        fields = [
            'name', 'role', 'status', 'app_version', 'created_by',
            'created_after', 'created_before', 'expires_after', 'expires_before',
            'last_used_after', 'last_used_before', 'usage_count_min', 'usage_count_max',
            'is_expired', 'has_expiry', 'has_usage_limit'
        ]
    
    def filter_expired(self, queryset, name, value):
        """Filter tokens by expiry status"""
        from django.utils import timezone
        now = timezone.now()
        
        if value:
            # Return expired tokens
            return queryset.filter(
                models.Q(expires_at__lte=now) | 
                models.Q(status__in=['inactive', 'revoked'])
            )
        else:
            # Return active tokens
            return queryset.filter(
                models.Q(expires_at__gt=now) | models.Q(expires_at__isnull=True),
                status='active'
            )


class APIClientTokenFilter(django_filters.FilterSet):
    """
    Filter for API Client Tokens
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    client_name = django_filters.CharFilter(lookup_expr='icontains')
    client_email = django_filters.CharFilter(lookup_expr='icontains')
    client_organization = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=APIClientToken.STATUS_CHOICES)
    created_by = django_filters.CharFilter(field_name='created_by__username', lookup_expr='icontains')
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    expires_after = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='gte')
    expires_before = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='lte')
    last_used_after = django_filters.DateTimeFilter(field_name='last_used_at', lookup_expr='gte')
    last_used_before = django_filters.DateTimeFilter(field_name='last_used_at', lookup_expr='lte')
    
    # Usage filters
    usage_count_min = django_filters.NumberFilter(field_name='usage_count', lookup_expr='gte')
    usage_count_max = django_filters.NumberFilter(field_name='usage_count', lookup_expr='lte')
    
    # Rate limit filters
    rate_limit_per_hour_min = django_filters.NumberFilter(field_name='rate_limit_per_hour', lookup_expr='gte')
    rate_limit_per_hour_max = django_filters.NumberFilter(field_name='rate_limit_per_hour', lookup_expr='lte')
    rate_limit_per_day_min = django_filters.NumberFilter(field_name='rate_limit_per_day', lookup_expr='gte')
    rate_limit_per_day_max = django_filters.NumberFilter(field_name='rate_limit_per_day', lookup_expr='lte')
    
    # Boolean filters
    is_expired = django_filters.BooleanFilter(method='filter_expired')
    has_expiry = django_filters.BooleanFilter(field_name='expires_at', lookup_expr='isnull', exclude=True)
    has_usage_limit = django_filters.BooleanFilter(field_name='max_usage_count', lookup_expr='isnull', exclude=True)
    has_permissions = django_filters.BooleanFilter(method='filter_has_permissions')
    
    class Meta:
        model = APIClientToken
        fields = [
            'name', 'client_name', 'client_email', 'client_organization', 'status', 'created_by',
            'created_after', 'created_before', 'expires_after', 'expires_before',
            'last_used_after', 'last_used_before', 'usage_count_min', 'usage_count_max',
            'rate_limit_per_hour_min', 'rate_limit_per_hour_max', 'rate_limit_per_day_min', 'rate_limit_per_day_max',
            'is_expired', 'has_expiry', 'has_usage_limit', 'has_permissions'
        ]
    
    def filter_expired(self, queryset, name, value):
        """Filter tokens by expiry status"""
        from django.utils import timezone
        now = timezone.now()
        
        if value:
            # Return expired tokens
            return queryset.filter(
                models.Q(expires_at__lte=now) | 
                models.Q(status__in=['inactive', 'revoked'])
            )
        else:
            # Return active tokens
            return queryset.filter(
                models.Q(expires_at__gt=now) | models.Q(expires_at__isnull=True),
                status='active'
            )
    
    def filter_has_permissions(self, queryset, name, value):
        """Filter tokens by whether they have model permissions"""
        if value:
            return queryset.filter(model_permissions__isnull=False).distinct()
        else:
            return queryset.filter(model_permissions__isnull=True)


class TokenUsageLogFilter(django_filters.FilterSet):
    """
    Filter for Token Usage Logs
    """
    token_type = django_filters.ChoiceFilter(choices=TokenUsageLog.TOKEN_TYPE_CHOICES)
    token_name = django_filters.CharFilter(lookup_expr='icontains')
    endpoint = django_filters.CharFilter(lookup_expr='icontains')
    method = django_filters.CharFilter(lookup_expr='exact')
    ip_address = django_filters.CharFilter(lookup_expr='exact')
    
    # Status code filters
    status_code = django_filters.NumberFilter()
    status_code_min = django_filters.NumberFilter(field_name='status_code', lookup_expr='gte')
    status_code_max = django_filters.NumberFilter(field_name='status_code', lookup_expr='lte')
    success = django_filters.BooleanFilter(method='filter_success')
    client_error = django_filters.BooleanFilter(method='filter_client_error')
    server_error = django_filters.BooleanFilter(method='filter_server_error')
    
    # Response time filters
    response_time_min = django_filters.NumberFilter(field_name='response_time_ms', lookup_expr='gte')
    response_time_max = django_filters.NumberFilter(field_name='response_time_ms', lookup_expr='lte')
    slow_requests = django_filters.BooleanFilter(method='filter_slow_requests')
    
    # Date filters
    timestamp_after = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    timestamp_before = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    today = django_filters.BooleanFilter(method='filter_today')
    this_week = django_filters.BooleanFilter(method='filter_this_week')
    this_month = django_filters.BooleanFilter(method='filter_this_month')
    
    # Data size filters
    request_size_min = django_filters.NumberFilter(field_name='request_data_size', lookup_expr='gte')
    request_size_max = django_filters.NumberFilter(field_name='request_data_size', lookup_expr='lte')
    response_size_min = django_filters.NumberFilter(field_name='response_data_size', lookup_expr='gte')
    response_size_max = django_filters.NumberFilter(field_name='response_data_size', lookup_expr='lte')
    
    class Meta:
        model = TokenUsageLog
        fields = [
            'token_type', 'token_name', 'endpoint', 'method', 'ip_address',
            'status_code', 'status_code_min', 'status_code_max', 'success', 'client_error', 'server_error',
            'response_time_min', 'response_time_max', 'slow_requests',
            'timestamp_after', 'timestamp_before', 'today', 'this_week', 'this_month',
            'request_size_min', 'request_size_max', 'response_size_min', 'response_size_max'
        ]
    
    def filter_success(self, queryset, name, value):
        """Filter successful requests (2xx status codes)"""
        if value:
            return queryset.filter(status_code__gte=200, status_code__lt=300)
        else:
            return queryset.exclude(status_code__gte=200, status_code__lt=300)
    
    def filter_client_error(self, queryset, name, value):
        """Filter client error requests (4xx status codes)"""
        if value:
            return queryset.filter(status_code__gte=400, status_code__lt=500)
        else:
            return queryset.exclude(status_code__gte=400, status_code__lt=500)
    
    def filter_server_error(self, queryset, name, value):
        """Filter server error requests (5xx status codes)"""
        if value:
            return queryset.filter(status_code__gte=500, status_code__lt=600)
        else:
            return queryset.exclude(status_code__gte=500, status_code__lt=600)
    
    def filter_slow_requests(self, queryset, name, value):
        """Filter slow requests (>1000ms response time)"""
        if value:
            return queryset.filter(response_time_ms__gt=1000)
        else:
            return queryset.filter(response_time_ms__lte=1000)
    
    def filter_today(self, queryset, name, value):
        """Filter logs from today"""
        if value:
            from django.utils import timezone
            today = timezone.now().date()
            return queryset.filter(timestamp__date=today)
        return queryset
    
    def filter_this_week(self, queryset, name, value):
        """Filter logs from this week"""
        if value:
            from django.utils import timezone
            from datetime import timedelta
            week_ago = timezone.now().date() - timedelta(days=7)
            return queryset.filter(timestamp__date__gte=week_ago)
        return queryset
    
    def filter_this_month(self, queryset, name, value):
        """Filter logs from this month"""
        if value:
            from django.utils import timezone
            from datetime import timedelta
            month_ago = timezone.now().date() - timedelta(days=30)
            return queryset.filter(timestamp__date__gte=month_ago)
        return queryset