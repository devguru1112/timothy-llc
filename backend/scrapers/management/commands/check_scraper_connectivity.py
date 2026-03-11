"""
Check if the backend can reach scraping APIs (RemoteOK, USAJobs).
Run from the same machine as the Celery worker to verify network/connectivity.

Usage:
    cd backend && python manage.py check_scraper_connectivity
"""
import json
import requests
from django.core.management.base import BaseCommand

# Same headers as scrapers
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}


class Command(BaseCommand):
    help = "Check connectivity to RemoteOK and USAJobs APIs (same machine as Celery worker)"

    def handle(self, *args, **options):
        self.stdout.write("Checking scraper connectivity (run from same machine as Celery worker)\n")
        ok = True

        # 1. RemoteOK
        url = "https://remoteok.com/api"
        try:
            r = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
            text = (r.text or "").strip()
            if r.status_code != 200:
                self.stdout.write(self.style.ERROR(f"RemoteOK: HTTP {r.status_code}"))
                self.stdout.write(f"  Response (first 200 chars): {text[:200]}")
                ok = False
            elif not text:
                self.stdout.write(self.style.ERROR("RemoteOK: empty response"))
                ok = False
            else:
                try:
                    data = r.json()
                    n = len(data) if isinstance(data, list) else 0
                    # First item is often metadata
                    jobs = [x for x in (data if isinstance(data, list) else []) if isinstance(x, dict) and x.get("position")]
                    self.stdout.write(self.style.SUCCESS(f"RemoteOK: OK (status=200, {len(data)} raw items, ~{len(jobs)} jobs)"))
                except json.JSONDecodeError as e:
                    self.stdout.write(self.style.ERROR(f"RemoteOK: invalid JSON - {e}"))
                    ok = False
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"RemoteOK: request failed - {e}"))
            ok = False

        # 2. USAJobs (if settings exist)
        try:
            from projects.models import SystemSettings
            api_key = (SystemSettings.get_setting("usajobs_api_key") or "").strip()
            user_email = (SystemSettings.get_setting("usajobs_user_email") or "").strip()
            if not api_key or not user_email:
                self.stdout.write(self.style.WARNING("USAJobs: skipped (usajobs_api_key or usajobs_user_email not set)"))
            else:
                headers = {
                    **DEFAULT_HEADERS,
                    "Host": "data.usajobs.gov",
                    "User-Agent": user_email,
                    "Authorization-Key": api_key,
                }
                r = requests.get(
                    "https://data.usajobs.gov/api/Search",
                    headers=headers,
                    params={"Keyword": "Marketing", "ResultsPerPage": 5},
                    timeout=15,
                )
                if r.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"USAJobs: HTTP {r.status_code}"))
                    self.stdout.write(f"  Response: {(r.text or '')[:300]}")
                    ok = False
                else:
                    data = r.json()
                    items = (data.get("SearchResult") or {}).get("SearchResultItems") or []
                    self.stdout.write(self.style.SUCCESS(f"USAJobs: OK (status=200, {len(items)} jobs)"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"USAJobs: error - {e}"))
            ok = False

        self.stdout.write("")
        if ok:
            self.stdout.write(self.style.SUCCESS("Connectivity OK. If Celery still gets 0, restart the worker and ensure it runs with the same network (e.g. same host, not isolated Docker)."))
        else:
            self.stdout.write(self.style.WARNING("Some checks failed. Fix network/firewall or API keys, then run again."))
