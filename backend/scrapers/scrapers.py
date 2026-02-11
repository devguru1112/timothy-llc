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
        if isinstance(data, list):
            return self._parse_list_response(data, limit)
        if isinstance(data, dict):
            # Some APIs return { "jobs": [...], "meta": {} }
            for key in ('jobs', 'results', 'data', 'items', 'listings'):
                if key in data and isinstance(data[key], list):
                    return self._parse_list_response(data[key], limit)
        logger.warning("Unsupported API response shape: %s", type(data))
        return []
    
    def _parse_list_response(self, items: List[Any], limit: int) -> List[Dict]:
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
            source_id = str(item.get('id') or item.get('slug') or source_url.split('/')[-1] or '')
            projects.append({
                'title': title,
                'description': description,
                'source_url': source_url,
                'source_id': source_id,
            })
        return projects


def get_scraper(platform) -> BaseScraper:
    """Factory function to get appropriate scraper for platform."""
    scraping_method = platform.scraping_method
    rpm = max(1, getattr(platform, 'rate_limit_per_minute', 10) or 10)
    delay = 60 / rpm

    if scraping_method == 'rss_feed':
        return RSSFeedScraper(platform, rate_limit_delay=delay)
    elif scraping_method == 'public_api':
        return APIScraper(platform, rate_limit_delay=delay)
    elif scraping_method == 'public_scrape':
        return JobBoardScraper(platform, rate_limit_delay=delay)
    else:
        raise ValueError(f"Unknown scraping method: {scraping_method}")
