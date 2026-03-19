"""
Middleware to track application limits for non-authenticated users.
"""
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
from projects.models import SystemSettings


class ApplicationLimitMiddleware(MiddlewareMixin):
    """Track application submissions per email/IP."""
    
    def process_request(self, request):
        """Track application attempts."""
        # Only track for application submissions
        if request.path == '/api/projects/applications/' and request.method == 'POST':
            # Get application limit from settings
            limit = int(SystemSettings.get_setting('free_applications_limit', '3'))
            
            # Get identifier (email or IP)
            # Try to get from request body (for DRF JSON requests)
            email = None
            if hasattr(request, 'body') and request.body:
                try:
                    import json
                    body_data = json.loads(request.body)
                    email = body_data.get('applicant_email')
                except:
                    pass
            
            # Fallback to POST data
            if not email:
                email = request.POST.get('applicant_email')
            
            ip_address = self.get_client_ip(request)
            identifier = email or ip_address
            
            if identifier:
                cache_key = f'app_limit_{identifier}'
                count = cache.get(cache_key, 0)
                request.applications_remaining = max(0, limit - count)
                request.applications_limit = limit
                request.applications_exceeded = count >= limit
            else:
                request.applications_remaining = limit
                request.applications_limit = limit
                request.applications_exceeded = False
        
        return None
    
    def process_response(self, request, response):
        """Increment application count after successful submission."""
        if (request.path == '/api/projects/applications/' and 
            request.method == 'POST' and 
            response.status_code == 201):
            
            # Try to get email from request body
            email = None
            if hasattr(request, 'body') and request.body:
                try:
                    import json
                    body_data = json.loads(request.body)
                    email = body_data.get('applicant_email')
                except:
                    pass
            
            # Fallback to POST data
            if not email:
                email = request.POST.get('applicant_email')
            
            ip_address = self.get_client_ip(request)
            identifier = email or ip_address
            
            if identifier:
                cache_key = f'app_limit_{identifier}'
                count = cache.get(cache_key, 0)
                cache.set(cache_key, count + 1, timeout=86400)  # 24 hours
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ProjectViewLimitMiddleware(MiddlewareMixin):
    """
    Track unique project detail views for anonymous users (by IP) using cache.

    This closes the gap where list endpoints are limited, but anyone could open unlimited
    `/projects/leads/:id/` detail pages directly.
    """

    CACHE_TTL_SECONDS = 86400  # 24 hours

    def process_request(self, request):
        if request.method != 'GET':
            return None

        # Only enforce on project detail endpoint
        path = request.path or ''
        prefix = '/api/projects/leads/'
        if not (path.startswith(prefix) and path.endswith('/')):
            return None

        # If authenticated (or verified), backend already handles view tracking/limits elsewhere.
        user = getattr(request, 'user', None)
        if user and getattr(user, 'is_authenticated', False):
            return None

        # Extract numeric ID from /api/projects/leads/<id>/
        raw_id = path[len(prefix):-1]
        try:
            project_id = int(raw_id)
        except (TypeError, ValueError):
            return None

        limit = int(SystemSettings.get_setting('free_projects_limit', '10'))
        ip_address = self.get_client_ip(request)
        identifier = ip_address
        cache_key = f'proj_views_{identifier}'

        seen = cache.get(cache_key)
        if not isinstance(seen, (list, set, tuple)):
            seen = []
        seen_set = set(int(x) for x in seen if str(x).isdigit())

        already_seen = project_id in seen_set
        # Count is based on unique IDs
        count = len(seen_set)

        # If the user is trying to view a new project beyond the limit, block.
        if not already_seen and count >= limit:
            request.project_views_limit = limit
            request.project_views_count = count
            request.project_views_remaining = 0
            request.project_views_exceeded = True
            return JsonResponse(
                {
                    'error': 'Free project limit reached',
                    'message': f'You have reached the limit of {limit} free project views. Please unlock Pro Plan to continue.',
                    'view_stats': {
                        'count': count,
                        'limit': limit,
                        'remaining': 0,
                        'reached': True,
                    },
                    'requires_upgrade': True,
                },
                status=403,
            )

        # Otherwise, record if it is a new project.
        if not already_seen:
            seen_set.add(project_id)
            cache.set(cache_key, list(seen_set), timeout=self.CACHE_TTL_SECONDS)
            count = len(seen_set)

        request.project_views_limit = limit
        request.project_views_count = count
        request.project_views_remaining = max(0, limit - count)
        request.project_views_exceeded = count >= limit
        request.project_view_stats = {
            'count': count,
            'limit': limit,
            'remaining': max(0, limit - count),
            'reached': count >= limit,
        }
        return None

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
