from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ScrapingJob
from .serializers import ScrapingJobSerializer
from .tasks import scrape_platform, scrape_all_active_platforms
from projects.models import SourcePlatform, JobCategory


class ScrapingJobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ScrapingJob.objects.select_related('platform').all().order_by('-created_at')
    serializer_class = ScrapingJobSerializer

    @action(detail=False, methods=['post'])
    def scrape_platform(self, request):
        """Trigger scraping for a specific platform."""
        platform_id = request.data.get('platform_id')
        limit = request.data.get('limit', 50)
        category_ids = request.data.get('category_ids', None)
        
        if not platform_id:
            return Response({'error': 'platform_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate category IDs if provided
        if category_ids is not None:
            if not isinstance(category_ids, list):
                return Response({'error': 'category_ids must be a list'}, status=status.HTTP_400_BAD_REQUEST)
            # Verify categories exist
            valid_categories = JobCategory.objects.filter(id__in=category_ids, is_active=True)
            if valid_categories.count() != len(category_ids):
                return Response({'error': 'Invalid category IDs'}, status=status.HTTP_400_BAD_REQUEST)
            category_ids = list(valid_categories.values_list('id', flat=True))
        
        try:
            platform = SourcePlatform.objects.get(id=platform_id, is_active=True)
            task = scrape_platform.delay(platform_id, limit, category_ids)
            return Response({
                'status': 'started',
                'platform': platform.name,
                'task_id': task.id,
                'category_ids': category_ids
            })
        except SourcePlatform.DoesNotExist:
            return Response({'error': 'Platform not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def scrape_all(self, request):
        """Trigger scraping for all active platforms."""
        limit = request.data.get('limit', 50)
        category_ids = request.data.get('category_ids', None)
        
        # Validate category IDs if provided
        if category_ids is not None:
            if not isinstance(category_ids, list):
                return Response({'error': 'category_ids must be a list'}, status=status.HTTP_400_BAD_REQUEST)
            # Verify categories exist
            valid_categories = JobCategory.objects.filter(id__in=category_ids, is_active=True)
            if valid_categories.count() != len(category_ids):
                return Response({'error': 'Invalid category IDs'}, status=status.HTTP_400_BAD_REQUEST)
            category_ids = list(valid_categories.values_list('id', flat=True))
        
        task = scrape_all_active_platforms.delay(limit, category_ids)
        return Response({
            'status': 'started',
            'task_id': task.id,
            'category_ids': category_ids
        })
