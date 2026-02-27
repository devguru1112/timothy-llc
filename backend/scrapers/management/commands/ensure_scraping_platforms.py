"""
Ensure RemoteOK, USAJobs, and ITJobPro source platforms exist for scraping.

Usage:
    python manage.py ensure_scraping_platforms
"""
from django.core.management.base import BaseCommand
from projects.models import SourcePlatform


# RemoteOK, USAJobs, ITJobPro – used by backend scrapers
SCRAPING_PLATFORMS = [
    {
        "name": "RemoteOK",
        "url": "https://remoteok.com/api",
        "user_count": 500000,
        "scraping_method": "public_api",
        "rate_limit_per_minute": 10,
        "is_active": True,
    },
    {
        "name": "USAJobs",
        "url": "https://data.usajobs.gov/api/search",
        "user_count": 2000000,
        "scraping_method": "public_api",
        "rate_limit_per_minute": 10,
        "is_active": True,
    },
    {
        "name": "ITJobPro",
        "url": "https://itjobpro.com/jobs/",
        "user_count": 100000,
        "scraping_method": "public_scrape",
        "rate_limit_per_minute": 5,
        "is_active": True,
    },
]


class Command(BaseCommand):
    help = "Add or update RemoteOK, USAJobs, and ITJobPro as source platforms for scraping"

    def handle(self, *args, **options):
        created = 0
        for data in SCRAPING_PLATFORMS:
            platform, was_created = SourcePlatform.objects.update_or_create(
                name=data["name"],
                defaults={
                    "url": data["url"],
                    "user_count": data["user_count"],
                    "scraping_method": data["scraping_method"],
                    "rate_limit_per_minute": data["rate_limit_per_minute"],
                    "is_active": data["is_active"],
                },
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {platform.name}"))
            else:
                self.stdout.write(f"Updated: {platform.name}")
        self.stdout.write(self.style.SUCCESS(f"\nDone. {created} created, {len(SCRAPING_PLATFORMS) - created} updated."))
