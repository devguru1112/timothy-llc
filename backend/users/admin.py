from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'is_community_member', 'priority_level', 'created_at']
    list_filter = ['is_community_member', 'is_staff', 'is_superuser']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'bio', 'skills', 'portfolio_url', 
                                        'is_community_member', 'priority_level')}),
    )
