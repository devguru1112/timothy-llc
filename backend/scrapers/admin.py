from django.contrib import admin
from .models import ScrapingJob


@admin.register(ScrapingJob)
class ScrapingJobAdmin(admin.ModelAdmin):
    list_display = ['platform', 'status', 'projects_found', 'projects_added', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'started_at', 'completed_at']
    date_hierarchy = 'created_at'
