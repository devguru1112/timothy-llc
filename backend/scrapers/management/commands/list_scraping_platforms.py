"""
List scraping platforms with IDs for use with test_scraper.

Usage:
    python manage.py list_scraping_platforms

Then test a scraper with:
    python manage.py test_scraper <id> --limit 5
"""
from django.core.management.base import BaseCommand
from projects.models import SourcePlatform


class Command(BaseCommand):
    help = 'List scraping platforms (ID, name, URL) for test_scraper'

    def handle(self, *args, **options):
        platforms = SourcePlatform.objects.filter(is_active=True).order_by('id')
        if not platforms.exists():
            self.stdout.write(self.style.WARNING('No active platforms. Run: python manage.py ensure_scraping_platforms'))
            return
        self.stdout.write('ID  Name              URL')
        self.stdout.write('-' * 70)
        for p in platforms:
            url = (p.url or '')[:52] + ('...' if len(p.url or '') > 52 else '')
            self.stdout.write(f'{p.id:<4} {p.name or "":<17} {url}')
        self.stdout.write('')
        self.stdout.write('Test a scraper:  python manage.py test_scraper <id> --limit 5')
        self.stdout.write('Example:         python manage.py test_scraper 1 --limit 5')
