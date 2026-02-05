from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import ProjectLead, SourcePlatform, ProjectMatch
from .serializers import (
    ProjectLeadSerializer, 
    ProjectLeadListSerializer,
    SourcePlatformSerializer,
    ProjectMatchSerializer
)
from .services import ProjectMatchingService


class SourcePlatformViewSet(viewsets.ModelViewSet):
    queryset = SourcePlatform.objects.all()
    serializer_class = SourcePlatformSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active', 'scraping_method']
    search_fields = ['name']


class ProjectLeadViewSet(viewsets.ModelViewSet):
    queryset = ProjectLead.objects.select_related('source_platform', 'matched_user').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'source_platform', 'matched_user']
    search_fields = ['title', 'description', 'company_name', 'contact_name']
    ordering_fields = ['relevance_score', 'quality_score', 'scraped_at', 'created_at']
    ordering = ['-relevance_score', '-scraped_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectLeadListSerializer
        return ProjectLeadSerializer

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
