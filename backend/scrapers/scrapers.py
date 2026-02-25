"""
Scrapers for various compliant sources.
Focuses on publicly available data, RSS feeds, and APIs.
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Lazy import to avoid circular dependency
def _get_system_settings():
    from projects.models import SystemSettings
    return SystemSettings

# Browser-like headers to reduce 403 from bot-sensitive feeds (e.g. Stack Overflow, Cloudflare).
DEFAULT_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


class BaseScraper:
    """Base class for all scrapers."""
    
    def __init__(self, platform, rate_limit_delay=6):
        self.platform = platform
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
    
    def scrape(self, limit: int = 50) -> List[Dict]:
        """Main scraping method to be implemented by subclasses."""
        raise NotImplementedError
    
    def _delay(self):
        """Respect rate limits."""
        time.sleep(self.rate_limit_delay)


class RSSFeedScraper(BaseScraper):
    """Scraper for RSS/Atom feeds."""
    
    def scrape(self, limit: int = 50) -> List[Dict]:
        """Scrape projects from RSS feed."""
        try:
            # Use RSS-friendly Accept to improve compatibility with some feeds
            headers = {'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml, */*;q=0.9'}
            response = self.session.get(self.platform.url, timeout=30, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')[:limit]
            
            projects = []
            for item in items:
                project = self._parse_rss_item(item)
                if project:
                    projects.append(project)
                self._delay()
            
            return projects
        except Exception as e:
            logger.error(f"Error scraping RSS feed {self.platform.url}: {e}")
            return []
    
    def _parse_rss_item(self, item) -> Optional[Dict]:
        """Parse a single RSS item into project data."""
        try:
            title = item.find('title')
            description = item.find('description')
            link = item.find('link')
            
            if not title or not link:
                return None
            
            return {
                'title': title.get_text().strip(),
                'description': description.get_text().strip() if description else '',
                'source_url': link.get_text().strip(),
                'source_id': link.get_text().strip().split('/')[-1],
            }
        except Exception as e:
            logger.error(f"Error parsing RSS item: {e}")
            return None


class JobBoardScraper(BaseScraper):
    """Scraper for public job boards (example structure)."""
    
    def scrape(self, limit: int = 50) -> List[Dict]:
        """Scrape projects from job board."""
        # This is a template - actual implementation would depend on specific job board
        # For compliance, only scrape publicly available listings
        try:
            response = self.session.get(self.platform.url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            # Implementation would parse specific HTML structure
            # This is a placeholder
            return []
        except Exception as e:
            logger.error(f"Error scraping job board {self.platform.url}: {e}")
            return []


class APIScraper(BaseScraper):
    """Scraper for platforms with public APIs (e.g. RemoteOK)."""
    
    def scrape(self, limit: int = 50) -> List[Dict]:
        """Scrape projects from API."""
        try:
            # Many job APIs (e.g. RemoteOK) use a single JSON endpoint without limit param
            url = self.platform.url
            if 'remoteok.com' in url or 'remoteok.com/json' in url:
                response = self.session.get(url, timeout=30)
            else:
                response = self.session.get(url, params={'limit': limit}, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            projects = self._parse_api_response(data, limit)
            return projects
        except Exception as e:
            logger.error(f"Error scraping API {self.platform.url}: {e}")
            return []
    
    def _parse_api_response(self, data: Any, limit: int = 50) -> List[Dict]:
        """Parse API response into project format. Supports RemoteOK and generic list-of-dicts."""
        base_url = None
        if 'remoteok.com' in getattr(self.platform, 'url', ''):
            base_url = 'https://remoteok.com'
        if isinstance(data, list):
            return self._parse_list_response(data, limit, base_url=base_url)
        if isinstance(data, dict):
            # Some APIs return { "jobs": [...], "meta": {} }
            for key in ('jobs', 'results', 'data', 'items', 'listings'):
                if key in data and isinstance(data[key], list):
                    return self._parse_list_response(data[key], limit, base_url=base_url)
        logger.warning("Unsupported API response shape: %s", type(data))
        return []
    
    def _parse_list_response(self, items: List[Any], limit: int, base_url: Optional[str] = None) -> List[Dict]:
        """Parse a list of job items (RemoteOK-style or generic)."""
        projects = []
        for item in items:
            if len(projects) >= limit:
                break
            if not isinstance(item, dict):
                continue
            # RemoteOK: first element can be metadata (has 'legal', no 'position')
            if 'legal' in item or 'last_updated' in item and 'position' not in item:
                continue
            # RemoteOK and similar: position, company, description, url
            title = item.get('position') or item.get('title') or item.get('name')
            if not title:
                continue
            description = item.get('description') or item.get('body') or ''
            if isinstance(description, str) and description:
                # Strip HTML tags for plain-text description
                description = re.sub(r'<[^>]+>', ' ', description)
                description = ' '.join(description.split())[:2000]
            source_url = item.get('url') or item.get('apply_url') or item.get('link') or ''
            if base_url and source_url and not source_url.startswith('http'):
                source_url = base_url.rstrip('/') + '/' + source_url.lstrip('/')
            source_id = str(item.get('id') or item.get('slug') or source_url.split('/')[-1] or '')
            project = {
                'title': title,
                'description': description,
                'source_url': source_url,
                'source_id': source_id,
            }
            if item.get('company'):
                project['company_name'] = item.get('company')
            projects.append(project)
        return projects


# ---------------------------------------------------------------------------
# USAJobs (official API) – requires API key in System Settings
# ---------------------------------------------------------------------------
USAJOBS_API_URL = "https://data.usajobs.gov/api/search"
# Default keywords used when no scraping config categories are available
USAJOBS_DEFAULT_KEYWORDS = ["Marketing", "SEO", "Social Media", "Digital Marketing", "Website Design", "LinkedIn Management"]


class USAJobsScraper(BaseScraper):
    """Scraper for USAJobs.gov via official API. Requires usajobs_api_key and usajobs_user_email in System Settings."""

    def scrape(self, limit: int = 50) -> List[Dict]:
        SystemSettings = _get_system_settings()
        api_key = SystemSettings.get_setting('usajobs_api_key', '').strip()
        user_email = SystemSettings.get_setting('usajobs_user_email', '').strip()
        if not api_key or not user_email:
            logger.warning("USAJobs scraper: usajobs_api_key and usajobs_user_email must be set in System Settings")
            return []

        headers = {
            "Host": "data.usajobs.gov",
            "User-Agent": user_email,
            "Authorization-Key": api_key,
        }
        seen_urls = set()
        projects = []
        # Use a few keywords to get variety; cap results per keyword so we don't exceed limit heavily
        keywords = self._get_keywords()
        per_keyword = max(10, (limit // len(keywords)) + 1) if keywords else limit

        for keyword in keywords:
            if len(projects) >= limit:
                break
            try:
                params = {
                    "Keyword": keyword,
                    "LocationName": "United States",
                    "ResultsPerPage": min(per_keyword, 100),
                }
                response = self.session.get(USAJOBS_API_URL, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                self._delay()
            except Exception as e:
                logger.error(f"Error fetching USAJobs for keyword '{keyword}': {e}")
                continue

            for item in data.get("SearchResult", {}).get("SearchResultItems", []):
                if len(projects) >= limit:
                    break
                try:
                    job = item.get("MatchedObjectDescriptor", {})
                    url = job.get("PositionURI", "")
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    title = job.get("PositionTitle", "Untitled")
                    org = job.get("OrganizationName", "")
                    location = job.get("PositionLocationDisplay", "")
                    qual = job.get("QualificationSummary", "") or ""
                    desc_parts = [qual]
                    if location:
                        desc_parts.append(f"Location: {location}.")
                    description = " ".join(desc_parts).strip() or title
                    projects.append({
                        "title": title,
                        "description": description[:2000],
                        "source_url": url,
                        "source_id": job.get("PositionID", "") or url.split("/")[-1] or "",
                        "company_name": org or None,
                    })
                except Exception as e:
                    logger.debug(f"Error parsing USAJobs item: {e}")
                    continue

        return projects[:limit]

    def _get_keywords(self) -> List[str]:
        """Keywords to search: from active ScrapingConfig categories or defaults."""
        try:
            from projects.models import ScrapingConfig
            config = ScrapingConfig.objects.filter(is_active=True).first()
            if config:
                categories = config.categories.filter(is_active=True)
                if categories.exists():
                    return list(categories.values_list("name", flat=True))[:10]
        except Exception as e:
            logger.debug(f"Could not load scraping config for USAJobs keywords: {e}")
        return USAJOBS_DEFAULT_KEYWORDS


# ---------------------------------------------------------------------------
# ITJobPro (HTML + AJAX)
# ---------------------------------------------------------------------------
ITJOBPRO_BASE_URL = "https://itjobpro.com"
ITJOBPRO_JOBS_PAGE = f"{ITJOBPRO_BASE_URL}/jobs/"
ITJOBPRO_AJAX_URL = f"{ITJOBPRO_BASE_URL}/jm-ajax/get_listings/"
ITJOBPRO_DEFAULT_KEYWORDS = ["SEO", "Marketing", "Social Media", "Website Design", "LinkedIn Management"]


class ITJobProScraper(BaseScraper):
    """Scraper for ITJobPro.com via public job listing page and AJAX API."""

    def __init__(self, platform, rate_limit_delay=6):
        super().__init__(platform, rate_limit_delay)
        self.session.headers["X-Requested-With"] = "XMLHttpRequest"

    def scrape(self, limit: int = 50) -> List[Dict]:
        try:
            tokens = self._get_tokens()
        except Exception as e:
            logger.error(f"ITJobPro: failed to get tokens: {e}")
            return []

        seen_urls = set()
        projects = []
        keywords = self._get_keywords()

        for keyword in keywords:
            if len(projects) >= limit:
                break
            page = 1
            while len(projects) < limit:
                jobs = self._fetch_page(keyword, page, tokens)
                if not jobs:
                    break
                for job in jobs:
                    if len(projects) >= limit:
                        break
                    url = job.get("url", "")
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    if not url.startswith("http"):
                        url = ITJOBPRO_BASE_URL.rstrip("/") + "/" + url.lstrip("/")
                    title = job.get("title", "Untitled")
                    description = job.get("description", "") or title
                    company = job.get("company", "")
                    projects.append({
                        "title": title,
                        "description": description[:2000],
                        "source_url": url,
                        "source_id": url.rstrip("/").split("/")[-1] or "",
                        "company_name": company or None,
                    })
                page += 1
                self._delay()

        return projects[:limit]

    def _get_tokens(self) -> Dict[str, str]:
        r = self.session.get(ITJOBPRO_JOBS_PAGE, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        tokens = {}
        for inp in soup.select("input[type='hidden']"):
            name = inp.get("name")
            value = inp.get("value")
            if name and value:
                tokens[name] = value
        return tokens

    def _fetch_page(self, keyword: str, page: int, tokens: Dict[str, str]) -> List[Dict]:
        payload = {
            "search_keywords": keyword,
            "search_location": "",
            "per_page": 10,
            "page": page,
            "orderby": "date",
            "order": "DESC",
        }
        payload.update(tokens)
        r = self.session.post(ITJOBPRO_AJAX_URL, data=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        html_fragment = data.get("html", "")
        if not (html_fragment or "").strip():
            return []
        soup = BeautifulSoup(html_fragment, "html.parser")
        job_items = soup.select("li.list-item")
        jobs = []
        for job in job_items:
            title_tag = job.select_one(".list-item-title a")
            title = title_tag.get_text(strip=True) if title_tag else ""
            url = title_tag.get("href", "") if title_tag else ""
            company_el = job.select_one(".list-item-company")
            location_el = job.select_one(".list-item-location")
            company = company_el.get_text(strip=True) if company_el else ""
            location = location_el.get_text(strip=True) if location_el else ""
            desc = f"Location: {location}" if location else ""
            jobs.append({
                "title": title,
                "url": url,
                "company": company,
                "description": desc,
            })
        return jobs

    def _get_keywords(self) -> List[str]:
        try:
            from projects.models import ScrapingConfig
            config = ScrapingConfig.objects.filter(is_active=True).first()
            if config:
                categories = config.categories.filter(is_active=True)
                if categories.exists():
                    return list(categories.values_list("name", flat=True))[:10]
        except Exception as e:
            logger.debug(f"Could not load scraping config for ITJobPro keywords: {e}")
        return ITJOBPRO_DEFAULT_KEYWORDS


def get_scraper(platform) -> BaseScraper:
    """Factory function to get appropriate scraper for platform."""
    url = (platform.url or "").lower()
    rpm = max(1, getattr(platform, 'rate_limit_per_minute', 10) or 10)
    delay = 60 / rpm

    if "usajobs.gov" in url:
        return USAJobsScraper(platform, rate_limit_delay=delay)
    if "itjobpro.com" in url:
        return ITJobProScraper(platform, rate_limit_delay=delay)

    scraping_method = platform.scraping_method
    if scraping_method == 'rss_feed':
        return RSSFeedScraper(platform, rate_limit_delay=delay)
    elif scraping_method == 'public_api':
        return APIScraper(platform, rate_limit_delay=delay)
    elif scraping_method == 'public_scrape':
        return JobBoardScraper(platform, rate_limit_delay=delay)
    else:
        raise ValueError(f"Unknown scraping method: {scraping_method}")
