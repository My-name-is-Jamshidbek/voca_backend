from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import MobileAppToken, APIClientToken, TokenModelPermission, TokenUsageLog
from .serializers import (
    MobileAppTokenSerializer, MobileAppTokenCreateSerializer,
    APIClientTokenSerializer, APIClientTokenCreateSerializer, APIClientTokenUpdateSerializer,
    TokenModelPermissionSerializer, TokenUsageLogSerializer,
    TokenStatsSerializer, TokenValidationSerializer, BulkTokenActionSerializer
)


class MobileAppTokenViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Mobile App Tokens
    """
    queryset = MobileAppToken.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description', 'app_version__version_name']
    ordering_fields = ['created_at', 'updated_at', 'last_used_at', 'usage_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MobileAppTokenCreateSerializer
        return MobileAppTokenSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate token for mobile app"""
        token = self.get_object()
        old_token = token.token
        token.token = token.generate_token()
        token.save(update_fields=['token', 'updated_at'])
        
        return Response({
            'message': 'Token regenerated successfully',
            'new_token': token.token,
            'old_token_prefix': old_token[:8] + '...' if old_token else None
        })
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke mobile app token"""
        token = self.get_object()
        token.status = 'revoked'
        token.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'message': 'Token revoked successfully',
            'token': self.get_serializer(token).data
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate mobile app token"""
        token = self.get_object()
        token.status = 'active'
        token.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'message': 'Token activated successfully',
            'token': self.get_serializer(token).data
        })
    
    @action(detail=True, methods=['get'])
    def usage_stats(self, request, pk=None):
        """Get usage statistics for mobile app token"""
        token = self.get_object()
        
        # Get usage logs for this token
        logs = TokenUsageLog.objects.filter(
            token_type='mobile',
            token_id=str(token.id)
        )
        
        # Calculate statistics
        total_requests = logs.count()
        today = timezone.now().date()
        requests_today = logs.filter(timestamp__date=today).count()
        requests_this_week = logs.filter(
            timestamp__gte=today - timedelta(days=7)
        ).count()
        
        # Get status code distribution
        status_codes = logs.values('status_code').annotate(
            count=Count('status_code')
        ).order_by('-count')
        
        # Get most used endpoints
        endpoints = logs.values('endpoint').annotate(
            count=Count('endpoint')
        ).order_by('-count')[:10]
        
        return Response({
            'token_name': token.name,
            'total_requests': total_requests,
            'requests_today': requests_today,
            'requests_this_week': requests_this_week,
            'last_used_at': token.last_used_at,
            'status_codes': list(status_codes),
            'top_endpoints': list(endpoints)
        })
    
    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Perform bulk actions on mobile app tokens"""
        serializer = BulkTokenActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token_ids = serializer.validated_data['token_ids']
        action_type = serializer.validated_data['action']
        reason = serializer.validated_data.get('reason', '')
        
        tokens = MobileAppToken.objects.filter(id__in=token_ids)
        
        if action_type == 'activate':
            tokens.update(status='active')
        elif action_type == 'deactivate':
            tokens.update(status='inactive')
        elif action_type == 'revoke':
            tokens.update(status='revoked')
        elif action_type == 'delete':
            tokens.delete()
            return Response({
                'message': f'Successfully deleted {len(token_ids)} tokens',
                'action': action_type,
                'reason': reason
            })
        
        return Response({
            'message': f'Successfully {action_type}d {tokens.count()} tokens',
            'action': action_type,
            'reason': reason
        })


class APIClientTokenViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing API Client Tokens
    """
    queryset = APIClientToken.objects.prefetch_related('model_permissions').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description', 'client_name', 'client_email', 'client_organization']
    ordering_fields = ['created_at', 'updated_at', 'last_used_at', 'usage_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return APIClientTokenCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return APIClientTokenUpdateSerializer
        return APIClientTokenSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate token for API client"""
        token = self.get_object()
        old_token = token.token
        token.token = token.generate_token()
        token.save(update_fields=['token', 'updated_at'])
        
        return Response({
            'message': 'Token regenerated successfully',
            'new_token': token.token,
            'old_token_prefix': old_token[:8] + '...' if old_token else None
        })
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke API client token"""
        token = self.get_object()
        token.status = 'revoked'
        token.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'message': 'Token revoked successfully',
            'token': self.get_serializer(token).data
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate API client token"""
        token = self.get_object()
        token.status = 'active'
        token.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'message': 'Token activated successfully',
            'token': self.get_serializer(token).data
        })
    
    @action(detail=True, methods=['get', 'post', 'put'])
    def permissions(self, request, pk=None):
        """Manage model permissions for API client token"""
        token = self.get_object()
        
        if request.method == 'GET':
            permissions = token.model_permissions.all()
            serializer = TokenModelPermissionSerializer(permissions, many=True)
            return Response(serializer.data)
        
        elif request.method in ['POST', 'PUT']:
            # Clear existing permissions
            token.model_permissions.all().delete()
            
            # Create new permissions
            permissions_data = request.data.get('permissions', [])
            created_permissions = []
            
            for perm_data in permissions_data:
                perm_data['token'] = token.id
                serializer = TokenModelPermissionSerializer(data=perm_data)
                if serializer.is_valid():
                    permission = serializer.save()
                    created_permissions.append(permission)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = TokenModelPermissionSerializer(created_permissions, many=True)
            return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def usage_stats(self, request, pk=None):
        """Get usage statistics for API client token"""
        token = self.get_object()
        
        # Get usage logs for this token
        logs = TokenUsageLog.objects.filter(
            token_type='api',
            token_id=str(token.id)
        )
        
        # Calculate statistics
        total_requests = logs.count()
        today = timezone.now().date()
        requests_today = logs.filter(timestamp__date=today).count()
        requests_this_week = logs.filter(
            timestamp__gte=today - timedelta(days=7)
        ).count()
        
        # Get status code distribution
        status_codes = logs.values('status_code').annotate(
            count=Count('status_code')
        ).order_by('-count')
        
        # Get most used endpoints
        endpoints = logs.values('endpoint').annotate(
            count=Count('endpoint')
        ).order_by('-count')[:10]
        
        # Get hourly usage for today
        hourly_usage = []
        for hour in range(24):
            hour_start = timezone.now().replace(hour=hour, minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)
            count = logs.filter(
                timestamp__gte=hour_start,
                timestamp__lt=hour_end
            ).count()
            hourly_usage.append({'hour': hour, 'requests': count})
        
        return Response({
            'token_name': token.name,
            'client_name': token.client_name,
            'total_requests': total_requests,
            'requests_today': requests_today,
            'requests_this_week': requests_this_week,
            'last_used_at': token.last_used_at,
            'rate_limit_per_hour': token.rate_limit_per_hour,
            'rate_limit_per_day': token.rate_limit_per_day,
            'status_codes': list(status_codes),
            'top_endpoints': list(endpoints),
            'hourly_usage': hourly_usage
        })
    
    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Perform bulk actions on API client tokens"""
        serializer = BulkTokenActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token_ids = serializer.validated_data['token_ids']
        action_type = serializer.validated_data['action']
        reason = serializer.validated_data.get('reason', '')
        
        tokens = APIClientToken.objects.filter(id__in=token_ids)
        
        if action_type == 'activate':
            tokens.update(status='active')
        elif action_type == 'deactivate':
            tokens.update(status='inactive')
        elif action_type == 'revoke':
            tokens.update(status='revoked')
        elif action_type == 'delete':
            # Also delete related permissions
            TokenModelPermission.objects.filter(token__in=tokens).delete()
            tokens.delete()
            return Response({
                'message': f'Successfully deleted {len(token_ids)} tokens and their permissions',
                'action': action_type,
                'reason': reason
            })
        
        return Response({
            'message': f'Successfully {action_type}d {tokens.count()} tokens',
            'action': action_type,
            'reason': reason
        })


class TokenUsageLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing Token Usage Logs (read-only)
    """
    queryset = TokenUsageLog.objects.all()
    serializer_class = TokenUsageLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['token_name', 'endpoint', 'ip_address']
    ordering_fields = ['timestamp', 'response_time_ms', 'status_code']
    ordering = ['-timestamp']


class TokenValidationView(APIView):
    """
    View for validating tokens
    """
    permission_classes = []  # No authentication required for token validation
    
    def post(self, request):
        """Validate a token and return its details"""
        serializer = TokenValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token_value = serializer.validated_data['token']
        endpoint = serializer.validated_data.get('endpoint')
        method = serializer.validated_data.get('method')
        ip_address = serializer.validated_data.get('ip_address')
        
        # Determine token type and validate
        if token_value.startswith('mob_'):
            try:
                token = MobileAppToken.objects.get(token=token_value)
                token_type = 'mobile'
            except MobileAppToken.DoesNotExist:
                return Response({
                    'valid': False,
                    'error': 'Token not found'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        elif token_value.startswith('api_'):
            try:
                token = APIClientToken.objects.get(token=token_value)
                token_type = 'api'
            except APIClientToken.DoesNotExist:
                return Response({
                    'valid': False,
                    'error': 'Token not found'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        else:
            return Response({
                'valid': False,
                'error': 'Invalid token format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if token is valid
        if not token.is_valid():
            return Response({
                'valid': False,
                'error': 'Token is expired or inactive'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check IP restrictions
        if token.allowed_ips and ip_address:
            if ip_address not in token.allowed_ips:
                return Response({
                    'valid': False,
                    'error': 'IP address not allowed'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # For API tokens, check endpoint restrictions
        if token_type == 'api' and endpoint:
            if token.allowed_endpoints and endpoint not in token.allowed_endpoints:
                return Response({
                    'valid': False,
                    'error': 'Endpoint not allowed'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Increment usage counter
        token.increment_usage()
        
        # Prepare response data
        response_data = {
            'valid': True,
            'token_type': token_type,
            'token_name': token.name,
            'usage_count': token.usage_count,
        }
        
        if token_type == 'mobile':
            response_data.update({
                'role': token.role,
                'app_version': {
                    'id': token.app_version.id,
                    'version_name': token.app_version.version_name,
                    'platform': token.app_version.platform,
                }
            })
        elif token_type == 'api':
            response_data.update({
                'client_name': token.client_name,
                'rate_limit_per_hour': token.rate_limit_per_hour,
                'rate_limit_per_day': token.rate_limit_per_day,
            })
        
        return Response(response_data)


class TokenStatsView(APIView):
    """
    View for getting token statistics
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get comprehensive token statistics"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Count tokens
        total_mobile_tokens = MobileAppToken.objects.count()
        active_mobile_tokens = MobileAppToken.objects.filter(status='active').count()
        total_api_tokens = APIClientToken.objects.count()
        active_api_tokens = APIClientToken.objects.filter(status='active').count()
        
        # Usage statistics
        total_usage_today = TokenUsageLog.objects.filter(timestamp__date=today).count()
        total_usage_this_week = TokenUsageLog.objects.filter(timestamp__date__gte=week_ago).count()
        total_usage_this_month = TokenUsageLog.objects.filter(timestamp__date__gte=month_ago).count()
        
        # Most used endpoints
        most_used_endpoints = list(
            TokenUsageLog.objects.filter(timestamp__date__gte=week_ago)
            .values('endpoint')
            .annotate(count=Count('endpoint'))
            .order_by('-count')[:10]
        )
        
        # Recent activity (last 10 usage logs)
        recent_activity = TokenUsageLog.objects.select_related().order_by('-timestamp')[:10]
        recent_activity_data = TokenUsageLogSerializer(recent_activity, many=True).data
        
        stats_data = {
            'total_mobile_tokens': total_mobile_tokens,
            'active_mobile_tokens': active_mobile_tokens,
            'total_api_tokens': total_api_tokens,
            'active_api_tokens': active_api_tokens,
            'total_usage_today': total_usage_today,
            'total_usage_this_week': total_usage_this_week,
            'total_usage_this_month': total_usage_this_month,
            'most_used_endpoints': most_used_endpoints,
            'recent_activity': recent_activity_data,
        }
        
        serializer = TokenStatsSerializer(stats_data)
        return Response(serializer.data)
