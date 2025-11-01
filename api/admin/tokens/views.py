from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models

from apps.tokens.models import MobileAppToken, APIClientToken, TokenModelPermission
from apps.tokens.serializers import (
    MobileAppTokenSerializer, MobileAppTokenCreateSerializer,
    APIClientTokenSerializer, APIClientTokenCreateSerializer, APIClientTokenUpdateSerializer,
    TokenModelPermissionSerializer
)
from apps.tokens.filters import MobileAppTokenFilter, APIClientTokenFilter


class AdminMobileAppTokenViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for managing Mobile App Tokens
    Full CRUD operations for administrators
    """
    queryset = MobileAppToken.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MobileAppTokenFilter
    search_fields = ['name', 'description', 'app_version__version_name', 'created_by__username']
    ordering_fields = ['created_at', 'updated_at', 'last_used_at', 'usage_count', 'expires_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MobileAppTokenCreateSerializer
        return MobileAppTokenSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get comprehensive statistics for mobile app tokens"""
        queryset = self.get_queryset()
        
        stats = {
            'total_tokens': queryset.count(),
            'active_tokens': queryset.filter(status='active').count(),
            'inactive_tokens': queryset.filter(status='inactive').count(),
            'revoked_tokens': queryset.filter(status='revoked').count(),
            'tokens_by_role': {},
            'tokens_by_app_version': {},
            'usage_summary': {
                'total_usage': sum(token.usage_count for token in queryset),
                'average_usage': queryset.aggregate(avg_usage=models.Avg('usage_count'))['avg_usage'] or 0,
                'most_used_token': None,
                'least_used_token': None,
            }
        }
        
        # Tokens by role
        for role_code, role_name in MobileAppToken.ROLE_CHOICES:
            stats['tokens_by_role'][role_name] = queryset.filter(role=role_code).count()
        
        # Tokens by app version
        app_versions = queryset.values('app_version__version_name').annotate(
            count=models.Count('app_version')
        ).order_by('-count')
        stats['tokens_by_app_version'] = {
            version['app_version__version_name']: version['count'] 
            for version in app_versions
        }
        
        # Usage summary
        most_used = queryset.order_by('-usage_count').first()
        least_used = queryset.order_by('usage_count').first()
        
        if most_used:
            stats['usage_summary']['most_used_token'] = {
                'name': most_used.name,
                'usage_count': most_used.usage_count
            }
        
        if least_used:
            stats['usage_summary']['least_used_token'] = {
                'name': least_used.name,
                'usage_count': least_used.usage_count
            }
        
        return Response(stats)


class AdminAPIClientTokenViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for managing API Client Tokens
    Full CRUD operations for administrators
    """
    queryset = APIClientToken.objects.prefetch_related('model_permissions').all()
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = APIClientTokenFilter
    search_fields = [
        'name', 'description', 'client_name', 'client_email', 
        'client_organization', 'created_by__username'
    ]
    ordering_fields = [
        'created_at', 'updated_at', 'last_used_at', 'usage_count', 
        'rate_limit_per_hour', 'rate_limit_per_day', 'expires_at'
    ]
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return APIClientTokenCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return APIClientTokenUpdateSerializer
        return APIClientTokenSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get comprehensive statistics for API client tokens"""
        queryset = self.get_queryset()
        
        stats = {
            'total_tokens': queryset.count(),
            'active_tokens': queryset.filter(status='active').count(),
            'inactive_tokens': queryset.filter(status='inactive').count(),
            'revoked_tokens': queryset.filter(status='revoked').count(),
            'tokens_by_organization': {},
            'rate_limit_distribution': {
                'low': queryset.filter(rate_limit_per_hour__lt=100).count(),
                'medium': queryset.filter(rate_limit_per_hour__gte=100, rate_limit_per_hour__lt=1000).count(),
                'high': queryset.filter(rate_limit_per_hour__gte=1000).count(),
            },
            'permissions_summary': {
                'tokens_with_permissions': queryset.filter(model_permissions__isnull=False).distinct().count(),
                'tokens_without_permissions': queryset.filter(model_permissions__isnull=True).count(),
                'most_common_permissions': {},
            },
            'usage_summary': {
                'total_usage': sum(token.usage_count for token in queryset),
                'average_usage': queryset.aggregate(avg_usage=models.Avg('usage_count'))['avg_usage'] or 0,
                'most_used_token': None,
                'least_used_token': None,
            }
        }
        
        # Tokens by organization
        organizations = queryset.exclude(client_organization='').values('client_organization').annotate(
            count=models.Count('client_organization')
        ).order_by('-count')
        stats['tokens_by_organization'] = {
            org['client_organization']: org['count'] 
            for org in organizations if org['client_organization']
        }
        
        # Most common permissions
        permissions = TokenModelPermission.objects.values('model_name').annotate(
            count=models.Count('model_name')
        ).order_by('-count')[:10]
        stats['permissions_summary']['most_common_permissions'] = {
            perm['model_name']: perm['count'] 
            for perm in permissions
        }
        
        # Usage summary
        most_used = queryset.order_by('-usage_count').first()
        least_used = queryset.order_by('usage_count').first()
        
        if most_used:
            stats['usage_summary']['most_used_token'] = {
                'name': most_used.name,
                'client_name': most_used.client_name,
                'usage_count': most_used.usage_count
            }
        
        if least_used:
            stats['usage_summary']['least_used_token'] = {
                'name': least_used.name,
                'client_name': least_used.client_name,
                'usage_count': least_used.usage_count
            }
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def bulk_permissions_update(self, request):
        """Bulk update permissions for multiple tokens"""
        token_ids = request.data.get('token_ids', [])
        permissions_data = request.data.get('permissions', [])
        
        if not token_ids:
            return Response({'error': 'token_ids required'}, status=400)
        
        tokens = APIClientToken.objects.filter(id__in=token_ids)
        updated_count = 0
        
        for token in tokens:
            # Clear existing permissions
            token.model_permissions.all().delete()
            
            # Create new permissions
            for perm_data in permissions_data:
                TokenModelPermission.objects.create(token=token, **perm_data)
            
            updated_count += 1
        
        return Response({
            'message': f'Successfully updated permissions for {updated_count} tokens',
            'updated_tokens': updated_count
        })


class AdminTokenModelPermissionViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for managing Token Model Permissions
    """
    queryset = TokenModelPermission.objects.select_related('token').all()
    serializer_class = TokenModelPermissionSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['token__name', 'model_name', 'token__client_name']
    ordering_fields = ['created_at', 'updated_at', 'model_name']
    ordering = ['model_name', 'token__name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by token if provided
        token_id = self.request.query_params.get('token_id')
        if token_id:
            queryset = queryset.filter(token_id=token_id)
        
        # Filter by model if provided
        model_name = self.request.query_params.get('model_name')
        if model_name:
            queryset = queryset.filter(model_name=model_name)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_model(self, request):
        """Get permissions grouped by model"""
        queryset = self.get_queryset()
        
        models_data = {}
        for permission in queryset:
            model_name = permission.model_name
            if model_name not in models_data:
                models_data[model_name] = {
                    'model_name': model_name,
                    'total_tokens': 0,
                    'permissions': []
                }
            
            models_data[model_name]['total_tokens'] += 1
            models_data[model_name]['permissions'].append({
                'token_name': permission.token.name,
                'client_name': permission.token.client_name,
                'permissions': permission.get_permissions_summary()
            })
        
        return Response(list(models_data.values()))
    
    @action(detail=False, methods=['get'])
    def by_token(self, request):
        """Get permissions grouped by token"""
        queryset = self.get_queryset()
        
        tokens_data = {}
        for permission in queryset:
            token_id = str(permission.token.id)
            if token_id not in tokens_data:
                tokens_data[token_id] = {
                    'token_id': token_id,
                    'token_name': permission.token.name,
                    'client_name': permission.token.client_name,
                    'total_permissions': 0,
                    'models': []
                }
            
            tokens_data[token_id]['total_permissions'] += 1
            tokens_data[token_id]['models'].append({
                'model_name': permission.model_name,
                'permissions': permission.get_permissions_summary()
            })
        
        return Response(list(tokens_data.values()))