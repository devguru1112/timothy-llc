"""
URL configuration for project_matcher project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from scrapers.admin_views import scrape_now_view

urlpatterns = [
    path('admin/scrape-now/', admin.site.admin_view(scrape_now_view), name='admin_scrape_now'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/scrapers/', include('scrapers.urls')),
    path('api/outreach/', include('outreach.urls')),
    path('api/payments/', include('payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
