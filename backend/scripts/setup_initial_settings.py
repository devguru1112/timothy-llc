"""
Script to set up initial system settings.
Run with: python manage.py shell
>>> from scripts.setup_initial_settings import setup_settings
>>> setup_settings()
"""
from projects.models import SystemSettings
from django.contrib.auth import get_user_model

User = get_user_model()


def setup_settings():
    """Create initial system settings."""
    settings = [
        {
            'key': 'free_projects_limit',
            'value': '10',
            'description': 'Number of free projects shown to non-authenticated users',
        },
        {
            'key': 'free_applications_limit',
            'value': '3',
            'description': 'Number of free applications allowed before requiring registration',
        },
        {
            'key': 'usajobs_api_key',
            'value': 'irD2ZpgHzFc4imtXSvQeL5Ngf6Wu3Rl1HNrnGVBpyFU=',
            'description': 'USAJobs.gov API Authorization-Key (required for USAJobs scraper). Get one at https://www.usajobs.gov/Help/working-in-government/unique-hiring-paths/students/federal-internships/',
        },
        {
            'key': 'usajobs_user_email',
            'value': 'daniel.dimitar.lee@gmail.com',
            'description': 'Email used as User-Agent for USAJobs.gov API (required for USAJobs scraper).',
        },
    ]
    
    created_count = 0
    for setting_data in settings:
        setting, created = SystemSettings.objects.get_or_create(
            key=setting_data['key'],
            defaults={
                'value': setting_data['value'],
                'description': setting_data['description'],
            }
        )
        if created:
            created_count += 1
            print(f"Created setting: {setting.key} = {setting.value}")
        else:
            print(f"Setting already exists: {setting.key} = {setting.value}")
    
    print(f"\nCreated {created_count} new settings")
    return created_count


if __name__ == '__main__':
    setup_settings()
