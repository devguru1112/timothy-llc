from django.contrib import admin
from .models import (
    ProjectLead, SourcePlatform, ProjectMatch, 
    ProjectApplication, SystemSettings
)


@admin.register(SourcePlatform)
class SourcePlatformAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'user_count', 'scraping_method', 'created_at']
    list_filter = ['is_active', 'scraping_method']
    search_fields = ['name', 'url']


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'description', 'updated_at', 'updated_by']
    search_fields = ['key', 'value', 'description']
    readonly_fields = ['updated_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProjectLead)
class ProjectLeadAdmin(admin.ModelAdmin):
    list_display = ['title', 'source_platform', 'status', 'is_public', 'relevance_score', 
                   'quality_score', 'matched_user', 'scraped_at']
    list_filter = ['status', 'source_platform', 'matched_user', 'is_public']
    search_fields = ['title', 'description', 'company_name', 'contact_email']
    readonly_fields = ['scraped_at', 'created_at', 'updated_at']
    date_hierarchy = 'scraped_at'
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'source_platform', 'source_url', 'source_id')
        }),
        ('Contact Information', {
            'fields': ('contact_name', 'contact_email', 'contact_phone', 'company_name')
        }),
        ('Project Details', {
            'fields': ('budget_min', 'budget_max', 'budget_currency', 'skills_required', 'project_type')
        }),
        ('Scores & Status', {
            'fields': ('relevance_score', 'quality_score', 'status', 'is_public', 'matched_user')
        }),
        ('Timestamps', {
            'fields': ('scraped_at', 'qualified_at', 'contacted_at', 'responded_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectMatch)
class ProjectMatchAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'match_score', 'is_selected', 'created_at']
    list_filter = ['is_selected', 'created_at']
    search_fields = ['project__title', 'user__username']


@admin.register(ProjectApplication)
class ProjectApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant_name', 'applicant_email', 'project', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'project']
    search_fields = ['applicant_name', 'applicant_email', 'project__title']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Application Information', {
            'fields': ('project', 'applicant_name', 'applicant_email', 'applicant_phone', 
                      'applicant_portfolio', 'applicant_skills', 'cover_letter')
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes', 'user')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
