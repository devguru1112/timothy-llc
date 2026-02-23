from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ScrapingJob
from .serializers import ScrapingJobSerializer
from .tasks import scrape_platform, scrape_all_active_platforms
from projects.models import SourcePlatform, JobCategory, SystemSettings


def is_superuser(request):
    return request.user and request.user.is_authenticated and getattr(request.user, 'is_superuser', False)


class ScrapingJobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ScrapingJob.objects.select_related('platform').all().order_by('-created_at')
    serializer_class = ScrapingJobSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def scrape_platform(self, request):
        """Trigger scraping for a specific platform (admin only)."""
        if not is_superuser(request):
            return Response({'error': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
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
        """Trigger scraping for all active platforms (admin only)."""
        if not is_superuser(request):
            return Response({'error': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
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


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def scraping_schedule(request):
    """
    GET: Return current scraping schedule (enabled, time, limit).
    PATCH: Update schedule (admin only). Body: { "enabled": true, "time": "02:00", "limit": 50 }.
    """
    if request.method == 'GET':
        enabled = SystemSettings.get_setting('scraping_schedule_enabled', '1').strip() in ('1', 'true', 'yes')
        time_val = SystemSettings.get_setting('scraping_schedule_time', '02:00').strip() or '02:00'
        limit = SystemSettings.get_int_setting('scraping_schedule_limit', 50)
        return Response({
            'enabled': enabled,
            'time': time_val,
            'limit': limit,
        })

    if request.method == 'PATCH':
        if not is_superuser(request):
            return Response({'error': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data
        if 'enabled' in data:
            val = '1' if data.get('enabled') in (True, '1', 1) else '0'
            obj, _ = SystemSettings.objects.get_or_create(
                key='scraping_schedule_enabled',
                defaults={'value': val, 'description': 'Enable automatic scraping at scheduled time'}
            )
            obj.value = val
            obj.save()
        if 'time' in data:
            raw = str(data.get('time', '')).strip()
            if raw and ':' in raw:
                parts = raw.split(':', 2)
                try:
                    h, m = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
                    if 0 <= h <= 23 and 0 <= m <= 59:
                        time_val = f'{h:02d}:{m:02d}'
                        obj, _ = SystemSettings.objects.get_or_create(
                            key='scraping_schedule_time',
                            defaults={'value': time_val, 'description': 'Scheduled scrape time (24h HH:MM)'}
                        )
                        obj.value = time_val
                        obj.save()
                except (ValueError, TypeError):
                    pass
        if 'limit' in data:
            try:
                limit = int(data.get('limit', 50))
                if limit < 1:
                    limit = 1
                if limit > 500:
                    limit = 500
                obj, _ = SystemSettings.objects.get_or_create(
                    key='scraping_schedule_limit',
                    defaults={'value': str(limit), 'description': 'Max projects per platform for scheduled scrape'}
                )
                obj.value = str(limit)
                obj.save()
            except (ValueError, TypeError):
                pass
        # Return current state
        enabled = SystemSettings.get_setting('scraping_schedule_enabled', '1').strip() in ('1', 'true', 'yes')
        time_val = SystemSettings.get_setting('scraping_schedule_time', '02:00').strip() or '02:00'
        limit = SystemSettings.get_int_setting('scraping_schedule_limit', 50)
        return Response({
            'enabled': enabled,
            'time': time_val,
            'limit': limit,
        })
