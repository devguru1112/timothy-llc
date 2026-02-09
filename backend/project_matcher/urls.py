"""
URL configuration for project_matcher project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/scrapers/', include('scrapers.urls')),
    path('api/outreach/', include('outreach.urls')),
]
