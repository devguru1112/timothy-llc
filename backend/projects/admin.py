from django.contrib import admin
from .models import ProjectLead, SourcePlatform, ProjectMatch


@admin.register(SourcePlatform)
class SourcePlatformAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'user_count', 'scraping_method', 'created_at']
    list_filter = ['is_active', 'scraping_method']
    search_fields = ['name', 'url']


@admin.register(ProjectLead)
class ProjectLeadAdmin(admin.ModelAdmin):
    list_display = ['title', 'source_platform', 'status', 'relevance_score', 
                   'quality_score', 'matched_user', 'scraped_at']
    list_filter = ['status', 'source_platform', 'matched_user']
    search_fields = ['title', 'description', 'company_name', 'contact_email']
    readonly_fields = ['scraped_at', 'created_at', 'updated_at']
    date_hierarchy = 'scraped_at'


@admin.register(ProjectMatch)
class ProjectMatchAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'match_score', 'is_selected', 'created_at']
    list_filter = ['is_selected', 'created_at']
    search_fields = ['project__title', 'user__username']
