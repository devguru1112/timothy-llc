"""
Celery Beat schedule configuration for periodic tasks.
"""
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'scrape-all-platforms-daily': {
        'task': 'scrapers.tasks.scrape_all_active_platforms',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
        'kwargs': {'limit': 50}
    },
    'scrape-all-platforms-hourly': {
        'task': 'scrapers.tasks.scrape_all_active_platforms',
        'schedule': crontab(minute=0),  # Run every hour
        'kwargs': {'limit': 20}
    },
    'auto-match-qualified-projects': {
        'task': 'projects.tasks.auto_match_qualified_projects',
        'schedule': crontab(minute='*/30'),  # Run every 30 minutes
    },
}
