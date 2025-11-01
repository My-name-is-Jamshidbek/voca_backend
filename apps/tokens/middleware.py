import json
import time
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.urls import resolve
from django.db import models
from .models import MobileAppToken, APIClientToken, TokenUsageLog


class TokenAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to handle token authentication and logging
    """
    
    # Endpoints that don't require token authentication
    EXEMPT_PATHS = [
        '/admin/',
        '/api/auth/',
        '/api/tokens/validate/',
        '/api/docs/',
        '/api/schema/',
    ]
    
    def process_request(self, request):
        """Process incoming requests for token authentication"""
        
        # Skip authentication for exempt paths
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return None
        
        # Skip if user is already authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            return None
        
        # Get token from header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None
        
        token_value = auth_header.split(' ')[1] if len(auth_header.split(' ')) > 1 else ''
        
        if not token_value:
            return None
        
        # Store request start time for response time calculation
        request._token_start_time = time.time()
        
        # Validate token
        token_data = self.validate_token(token_value, request)
        
        if not token_data['valid']:
            return JsonResponse({
                'error': 'Invalid token',
                'message': token_data.get('error', 'Token validation failed')
            }, status=401)
        
        # Add token info to request
        request.token_data = token_data
        request.token_type = token_data['token_type']
        request.token_name = token_data['token_name']
        
        return None
    
    def process_response(self, request, response):
        """Process response and log token usage"""
        
        # Only log if token was used
        if hasattr(request, 'token_data') and hasattr(request, '_token_start_time'):
            self.log_token_usage(request, response)
        
        return response
    
    def validate_token(self, token_value, request):
        """Validate token and return token data"""
        
        # Get client IP
        ip_address = self.get_client_ip(request)
        endpoint = request.path
        method = request.method
        
        # Determine token type and validate
        if token_value.startswith('mob_'):
            try:
                token = MobileAppToken.objects.select_related('app_version').get(token=token_value)
                token_type = 'mobile'
            except MobileAppToken.DoesNotExist:
                return {'valid': False, 'error': 'Mobile token not found'}
        
        elif token_value.startswith('api_'):
            try:
                token = APIClientToken.objects.get(token=token_value)
                token_type = 'api'
            except APIClientToken.DoesNotExist:
                return {'valid': False, 'error': 'API token not found'}
        
        else:
            return {'valid': False, 'error': 'Invalid token format'}
        
        # Check if token is valid
        if not token.is_valid():
            return {'valid': False, 'error': 'Token is expired or inactive'}
        
        # Check IP restrictions
        if token.allowed_ips and ip_address not in token.allowed_ips:
            return {'valid': False, 'error': 'IP address not allowed'}
        
        # For API tokens, check endpoint restrictions
        if token_type == 'api' and token.allowed_endpoints:
            if endpoint not in token.allowed_endpoints:
                return {'valid': False, 'error': 'Endpoint not allowed'}
        
        # Check rate limits for API tokens
        if token_type == 'api':
            rate_limit_check = self.check_rate_limits(token, request)
            if not rate_limit_check['allowed']:
                return {'valid': False, 'error': rate_limit_check['error']}
        
        # Prepare token data
        token_data = {
            'valid': True,
            'token_type': token_type,
            'token_name': token.name,
            'token_id': str(token.id),
            'usage_count': token.usage_count,
        }
        
        if token_type == 'mobile':
            token_data.update({
                'role': token.role,
                'app_version': {
                    'id': token.app_version.id,
                    'version_name': token.app_version.version_name,
                    'platform': token.app_version.platform,
                }
            })
        elif token_type == 'api':
            token_data.update({
                'client_name': token.client_name,
                'rate_limit_per_hour': token.rate_limit_per_hour,
                'rate_limit_per_day': token.rate_limit_per_day,
            })
        
        return token_data
    
    def check_rate_limits(self, token, request):
        """Check if API token has exceeded rate limits"""
        now = timezone.now()
        
        # Check hourly limit
        hour_ago = now - timezone.timedelta(hours=1)
        hourly_usage = TokenUsageLog.objects.filter(
            token_type='api',
            token_id=str(token.id),
            timestamp__gte=hour_ago
        ).count()
        
        if hourly_usage >= token.rate_limit_per_hour:
            return {
                'allowed': False,
                'error': f'Hourly rate limit exceeded ({token.rate_limit_per_hour} requests/hour)'
            }
        
        # Check daily limit
        day_ago = now - timezone.timedelta(days=1)
        daily_usage = TokenUsageLog.objects.filter(
            token_type='api',
            token_id=str(token.id),
            timestamp__gte=day_ago
        ).count()
        
        if daily_usage >= token.rate_limit_per_day:
            return {
                'allowed': False,
                'error': f'Daily rate limit exceeded ({token.rate_limit_per_day} requests/day)'
            }
        
        return {'allowed': True}
    
    def log_token_usage(self, request, response):
        """Log token usage for analytics"""
        
        try:
            # Calculate response time
            response_time_ms = int((time.time() - request._token_start_time) * 1000)
            
            # Get request/response sizes
            request_size = len(request.body) if hasattr(request, 'body') else 0
            response_size = len(response.content) if hasattr(response, 'content') else 0
            
            # Create usage log
            TokenUsageLog.objects.create(
                token_type=request.token_data['token_type'],
                token_id=request.token_data['token_id'],
                token_name=request.token_data['token_name'],
                endpoint=request.path,
                method=request.method,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000],  # Limit length
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                request_data_size=request_size,
                response_data_size=response_size,
            )
            
            # Update token usage count
            if request.token_data['token_type'] == 'mobile':
                MobileAppToken.objects.filter(
                    id=request.token_data['token_id']
                ).update(
                    usage_count=models.F('usage_count') + 1,
                    last_used_at=timezone.now()
                )
            elif request.token_data['token_type'] == 'api':
                APIClientToken.objects.filter(
                    id=request.token_data['token_id']
                ).update(
                    usage_count=models.F('usage_count') + 1,
                    last_used_at=timezone.now()
                )
        
        except Exception as e:
            # Log error but don't break the response
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error logging token usage: {str(e)}")
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class TokenPermissionMiddleware(MiddlewareMixin):
    """
    Middleware to check model-level permissions for API client tokens
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Check model permissions for API client tokens"""
        
        # Only check for API tokens
        if not hasattr(request, 'token_data') or request.token_data.get('token_type') != 'api':
            return None
        
        # Try to resolve the view to get model information
        try:
            resolved = resolve(request.path)
            view_class = getattr(view_func, 'cls', None)
            
            if view_class and hasattr(view_class, 'queryset'):
                model = view_class.queryset.model
                model_name = model.__name__
                
                # Get token permissions for this model
                try:
                    token = APIClientToken.objects.get(id=request.token_data['token_id'])
                    permission = token.model_permissions.filter(model_name=model_name).first()
                    
                    if permission:
                        # Check CRUD permissions based on request method
                        method = request.method.upper()
                        
                        if method == 'GET' and resolved.url_name and 'list' in resolved.url_name:
                            if not permission.can_list:
                                return JsonResponse({
                                    'error': 'Permission denied',
                                    'message': f'Token does not have list permission for {model_name}'
                                }, status=403)
                        
                        elif method == 'GET':
                            if not permission.can_read:
                                return JsonResponse({
                                    'error': 'Permission denied',
                                    'message': f'Token does not have read permission for {model_name}'
                                }, status=403)
                        
                        elif method == 'POST':
                            if not permission.can_create:
                                return JsonResponse({
                                    'error': 'Permission denied',
                                    'message': f'Token does not have create permission for {model_name}'
                                }, status=403)
                        
                        elif method in ['PUT', 'PATCH']:
                            if not permission.can_update:
                                return JsonResponse({
                                    'error': 'Permission denied',
                                    'message': f'Token does not have update permission for {model_name}'
                                }, status=403)
                        
                        elif method == 'DELETE':
                            if not permission.can_delete:
                                return JsonResponse({
                                    'error': 'Permission denied',
                                    'message': f'Token does not have delete permission for {model_name}'
                                }, status=403)
                        
                        # Store permission info in request for potential field filtering
                        request.token_permissions = permission
                    
                    else:
                        # No specific permissions set for this model - deny by default
                        return JsonResponse({
                            'error': 'Permission denied',
                            'message': f'Token does not have permissions for {model_name}'
                        }, status=403)
                
                except APIClientToken.DoesNotExist:
                    return JsonResponse({
                        'error': 'Invalid token',
                        'message': 'API token not found'
                    }, status=401)
        
        except Exception:
            # If we can't resolve permissions, allow the request to continue
            # The view itself will handle authorization
            pass
        
        return None