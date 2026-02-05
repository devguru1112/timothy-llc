from django.contrib import admin
from .models import OutreachTemplate, OutreachMessage


@admin.register(OutreachTemplate)
class OutreachTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'created_by', 'created_at']
    list_filter = ['is_default', 'created_at']


@admin.register(OutreachMessage)
class OutreachMessageAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'recipient_email', 'status', 'sent_at', 'created_at']
    list_filter = ['status', 'sent_at']
    search_fields = ['recipient_email', 'project__title']
    readonly_fields = ['created_at', 'updated_at', 'sent_at', 'opened_at', 'responded_at']
