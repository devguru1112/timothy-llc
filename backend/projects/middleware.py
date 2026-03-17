"""
Middleware to track application limits for non-authenticated users.
"""
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
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
