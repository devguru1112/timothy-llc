from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import (
    ProjectLead, SourcePlatform, ProjectMatch, 
    ProjectApplication, SystemSettings
)
from .serializers import (
    ProjectLeadSerializer, 
    ProjectLeadListSerializer,
    ProjectLeadPublicSerializer,
    SourcePlatformSerializer,
    ProjectMatchSerializer,
    ProjectApplicationSerializer,
    ProjectApplicationCreateSerializer,
    SystemSettingsSerializer,
)
from .services import ProjectMatchingService


class SourcePlatformViewSet(viewsets.ModelViewSet):
    queryset = SourcePlatform.objects.all()
    serializer_class = SourcePlatformSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active', 'scraping_method']
    search_fields = ['name']


class SystemSettingsViewSet(viewsets.ModelViewSet):
    """Admin-only viewset for system settings."""
    queryset = SystemSettings.objects.all()
    serializer_class = SystemSettingsSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users (admin)
    
    def get_queryset(self):
        # Only superusers can manage settings
        if self.request.user.is_superuser:
            return SystemSettings.objects.all()
        return SystemSettings.objects.none()


class ProjectLeadViewSet(viewsets.ModelViewSet):
    queryset = ProjectLead.objects.select_related('source_platform', 'matched_user').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'source_platform', 'matched_user', 'is_public']
    search_fields = ['title', 'description', 'company_name', 'contact_name']
    ordering_fields = ['relevance_score', 'quality_score', 'scraped_at', 'created_at']
    ordering = ['-relevance_score', '-scraped_at']

    def get_permissions(self):
        """Allow public access for list and retrieve, require auth for other actions."""
        if self.action in ['list', 'retrieve', 'public']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'list':
            if self.request.user.is_authenticated:
                return ProjectLeadListSerializer
            else:
                return ProjectLeadPublicSerializer
        elif self.action == 'retrieve':
            if self.request.user.is_authenticated:
                return ProjectLeadSerializer
            else:
                return ProjectLeadPublicSerializer
        return ProjectLeadSerializer

    def get_queryset(self):
        """Filter queryset based on authentication and verification status."""
        queryset = super().get_queryset()
        
        if not self.request.user.is_authenticated:
            # For anonymous users, only show public projects
            queryset = queryset.filter(is_public=True, status__in=['new', 'qualified'])
            
            # Limit to free projects count
            free_limit = SystemSettings.get_int_setting('free_projects_limit', 10)
            queryset = queryset[:free_limit]
        else:
            # Authenticated users
            user = self.request.user
            if user.is_fully_verified:
                # Fully verified users see all projects
                queryset = queryset.all()
            else:
                # Unverified users see limited projects
                queryset = queryset.filter(is_public=True, status__in=['new', 'qualified'])
                free_limit = SystemSettings.get_int_setting('free_projects_limit', 10)
                queryset = queryset[:free_limit]
        
        return queryset

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def public(self, request):
        """Public endpoint for browsing free projects (no authentication required)."""
        free_limit = SystemSettings.get_int_setting('free_projects_limit', 10)
        
        # Check if user is authenticated and verified
        if request.user.is_authenticated and hasattr(request.user, 'is_fully_verified') and request.user.is_fully_verified:
            # Fully verified users see all projects
            queryset = ProjectLead.objects.filter(
                status__in=['new', 'qualified']
            ).select_related('source_platform')
            limit = None
        else:
            # Non-authenticated or unverified users see limited projects
            queryset = ProjectLead.objects.filter(
                is_public=True,
                status__in=['new', 'qualified']
            ).select_related('source_platform')[:free_limit]
            limit = free_limit
        
        serializer = ProjectLeadPublicSerializer(queryset, many=True)
        return Response({
            'count': len(queryset),
            'limit': limit,
            'results': serializer.data
        })

    @action(detail=True, methods=['post'])
    def qualify(self, request, pk=None):
        """Manually trigger qualification of a project."""
        project = self.get_object()
        # This would call an AI service to re-qualify
        # For now, just return success
        return Response({'status': 'qualified', 'project_id': project.id})

    @action(detail=True, methods=['post'])
    def match(self, request, pk=None):
        """Find and create matches for this project with community members."""
        project = self.get_object()
        matching_service = ProjectMatchingService()
        matches = matching_service.find_matches(project)
        return Response({
            'project_id': project.id,
            'matches_found': len(matches),
            'matches': ProjectMatchSerializer(matches, many=True).data
        })

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get projects available for matching (not yet matched)."""
        queryset = self.get_queryset().filter(
            Q(status__in=['new', 'qualified']) & Q(matched_user__isnull=True)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_projects(self, request):
        """Get projects matched to the current user."""
        queryset = self.get_queryset().filter(matched_user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProjectMatchViewSet(viewsets.ModelViewSet):
    queryset = ProjectMatch.objects.select_related('project', 'user').all()
    serializer_class = ProjectMatchSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'project', 'is_selected']
    ordering_fields = ['match_score', 'created_at']
    ordering = ['-match_score']

    @action(detail=True, methods=['post'])
    def select(self, request, pk=None):
        """Select a match (assign project to user)."""
        match = self.get_object()
        match.is_selected = True
        match.project.matched_user = match.user
        match.project.status = 'matched'
        match.project.save()
        match.save()
        return Response(ProjectMatchSerializer(match).data)


class ProjectApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for project applications."""
    queryset = ProjectApplication.objects.select_related('project', 'user').all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'project']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        """Allow public access for create, require auth for list/retrieve."""
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectApplicationCreateSerializer
        return ProjectApplicationSerializer

    def create(self, request, *args, **kwargs):
        """Create a new application (no authentication required)."""
        # Check application limit for non-authenticated users
        if not request.user.is_authenticated:
            if hasattr(request, 'applications_exceeded') and request.applications_exceeded:
                return Response(
                    {
                        'error': 'Application limit reached',
                        'message': f'You have reached the limit of {request.applications_limit} free applications. Please register to continue.',
                        'applications_remaining': 0,
                        'requires_registration': True
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if user already applied to this project (by email)
        project = serializer.validated_data['project']
        applicant_email = serializer.validated_data['applicant_email']
        
        existing_application = ProjectApplication.objects.filter(
            project=project,
            applicant_email=applicant_email
        ).first()
        
        if existing_application:
            return Response(
                {'error': 'You have already applied to this project.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        application = serializer.save()
        
        # If user is authenticated, link the application to their account
        if request.user.is_authenticated:
            application.user = request.user
            application.save()
        
        # Include remaining applications in response
        response_data = ProjectApplicationSerializer(application).data
        if not request.user.is_authenticated:
            response_data['applications_remaining'] = getattr(request, 'applications_remaining', 0)
            response_data['applications_limit'] = getattr(request, 'applications_limit', 3)
        
        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )

    def get_queryset(self):
        """Filter applications based on user."""
        queryset = super().get_queryset()
        
        if self.request.user.is_authenticated:
            # Users can see their own applications
            # Admins can see all applications
            if self.request.user.is_superuser:
                return queryset
            return queryset.filter(user=self.request.user)
        
        # Non-authenticated users cannot list applications
        return ProjectApplication.objects.none()
