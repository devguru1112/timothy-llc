"""
Custom Django admin views for scrapers (e.g. Scrape now button).
"""
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

from .tasks import scrape_all_active_platforms


@require_http_methods(['GET', 'POST'])
@csrf_protect
def scrape_now_view(request):
    """
    Admin view: show "Scrape now" button; on POST trigger scraping and redirect with message.
    """
    if request.method == 'POST':
        limit = 50
        try:
            scrape_all_active_platforms.delay(limit=limit)
            messages.success(
                request,
                f'Scraping started in the background (limit {limit} per platform). '
                'Check Scraping jobs for status.'
            )
        except Exception as e:
            messages.error(request, f'Failed to start scraping: {e}')
        return redirect('admin_scrape_now')

    return render(request, 'admin/scrapers/scrape_now.html', {
        'title': 'Run scraping now',
    })
