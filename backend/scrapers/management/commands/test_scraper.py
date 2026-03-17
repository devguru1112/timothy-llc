"""
Django management command to test a scraper.

Usage:
    python manage.py test_scraper <platform_id> [--limit LIMIT]
"""
from django.core.management.base import BaseCommand, CommandError
from projects.models import SourcePlatform
from scrapers.scrapers import get_scraper


class Command(BaseCommand):
    help = 'Test a scraper for a specific platform'

    def add_arguments(self, parser):
        parser.add_argument('platform_id', type=int, help='ID of the platform to test')
        parser.add_argument(
            '--limit',
            type=int,
            default=5,
            help='Number of projects to scrape (default: 5)',
        )

    def handle(self, *args, **options):
        platform_id = options['platform_id']
        limit = options['limit']

        try:
            platform = SourcePlatform.objects.get(id=platform_id)
        except SourcePlatform.DoesNotExist:
            raise CommandError(f'Platform with ID {platform_id} does not exist')

        self.stdout.write(f'Testing scraper for: {platform.name}')
        self.stdout.write(f'URL: {platform.url}')
        self.stdout.write(f'Method: {platform.scraping_method}')
        self.stdout.write(f'Limit: {limit}')
        self.stdout.write('-' * 50)

        try:
            scraper = get_scraper(platform)
            projects = scraper.scrape(limit=limit)

            if not projects:
                self.stdout.write(self.style.WARNING('No projects found'))
                return

            self.stdout.write(self.style.SUCCESS(f'Found {len(projects)} projects:\n'))

            for i, project in enumerate(projects, 1):
                self.stdout.write(f'{i}. {project.get("title", "No title")}')
                self.stdout.write(f'   URL: {project.get("source_url", "No URL")}')
                if project.get("company_name"):
                    self.stdout.write(f'   Company: {project.get("company_name")}')
                if project.get("budget_min"):
                    self.stdout.write(f'   Budget: ${project.get("budget_min")} - ${project.get("budget_max", "N/A")}')
                if project.get("skills_required"):
                    self.stdout.write(f'   Skills: {", ".join(project.get("skills_required", []))}')
                self.stdout.write('')

            self.stdout.write(self.style.SUCCESS(f'\nSuccessfully scraped {len(projects)} projects!'))

        except Exception as e:
            raise CommandError(f'Error testing scraper: {e}')
