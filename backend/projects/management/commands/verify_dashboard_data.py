"""
Verify that project leads exist in the DB and dashboard counts would be correct.

Run from backend directory:
    python manage.py verify_dashboard_data

Use this to confirm:
  1. Scraped projects are saved (ProjectLead rows exist)
  2. Counts match what the dashboard API uses (available / matched)
"""
from django.core.management.base import BaseCommand
from django.db.models import Q, Count
from projects.models import ProjectLead, SourcePlatform
from outreach.models import OutreachMessage


class Command(BaseCommand):
    help = 'Verify project leads and dashboard counts in the database'

    def handle(self, *args, **options):
        total = ProjectLead.objects.count()
        available = ProjectLead.objects.filter(
            Q(status__in=['new', 'qualified']) & Q(matched_user__isnull=True)
        ).count()
        matched = ProjectLead.objects.filter(matched_user__isnull=False).count()
        by_status = dict(
            ProjectLead.objects.values('status').annotate(c=Count('id')).values_list('status', 'c')
        )
        platforms = SourcePlatform.objects.filter(is_active=True).count()
        outreach_sent = OutreachMessage.objects.filter(status='sent').count()

        self.stdout.write('--- Dashboard data verification ---')
        self.stdout.write(f'ProjectLead total: {total}')
        self.stdout.write(f'  available (new/qualified, unmatched): {available}')
        self.stdout.write(f'  matched (has matched_user): {matched}')
        if by_status:
            self.stdout.write(f'  by status: {by_status}')
        self.stdout.write(f'Active SourcePlatforms: {platforms}')
        self.stdout.write(f'OutreachMessage status=sent: {outreach_sent}')

        if total == 0:
            self.stdout.write(self.style.WARNING(
                '\nNo project leads in DB. Dashboard will show 0 until you add data:'
            ))
            self.stdout.write('  1. Sample data:  python manage.py create_sample_data')
            self.stdout.write('  2. Scraping:     python manage.py ensure_scraping_platforms')
            self.stdout.write('                  Then trigger a scrape from Dashboard → Scraping (or admin).')
        elif available == 0 and matched == 0:
            self.stdout.write(self.style.WARNING(
                '\nLeads exist but none are "available" or "matched". '
                'Check status values (expected: new, qualified, or matched with matched_user set).'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'\nDashboard would show: Available={available}, Matched={matched}, Outreach sent={outreach_sent}'
            ))
