# Scraping Guide - How to Scrape Project Data

This guide explains how to use the scraping system to collect project data from various sources.

## Table of Contents

1. [Overview](#overview)
2. [Setting Up Source Platforms](#setting-up-source-platforms)
3. [Triggering Scraping](#triggering-scraping)
4. [Scraping Methods](#scraping-methods)
5. [Creating Custom Scrapers](#creating-custom-scrapers)
6. [Testing Scraping](#testing-scraping)
7. [Troubleshooting](#troubleshooting)

## Overview

The scraping system supports three methods:
- **RSS Feed**: Scrape from RSS/Atom feeds
- **Public API**: Use public APIs to fetch data
- **Public Scraping**: Scrape publicly available HTML pages (compliant only)

All scraped projects are automatically:
- Qualified (scored for relevance and quality)
- Deduplicated (same URL won't be added twice)
- Stored in the database

## Setting Up Source Platforms

### Method 1: Via Django Admin

1. Go to `http://localhost:8000/admin`
2. Navigate to **Projects → Source Platforms**
3. Click **Add Source Platform**
4. Fill in the details:
   - **Name**: Platform name (e.g., "Stack Overflow Jobs")
   - **URL**: Feed/API endpoint URL
   - **User Count**: Approximate number of users
   - **Scraping Method**: Choose one:
     - `rss_feed` - For RSS/Atom feeds
     - `public_api` - For public APIs
     - `public_scrape` - For HTML scraping (use carefully)
     - `manual` - For manual entry only
   - **Rate Limit Per Minute**: How many requests per minute (default: 10)
   - **Is Active**: Check to enable scraping
5. Click **Save**

### Method 2: Via API

```bash
POST /api/projects/platforms/
Content-Type: application/json
Authorization: Bearer <your-token>

{
  "name": "Stack Overflow Jobs",
  "url": "https://stackoverflow.com/jobs/feed",
  "user_count": 2000000,
  "scraping_method": "rss_feed",
  "rate_limit_per_minute": 10,
  "is_active": true
}
```

### Method 3: Via Django Shell

```python
python manage.py shell

from projects.models import SourcePlatform

platform = SourcePlatform.objects.create(
    name="RemoteOK",
    url="https://remoteok.com/json",
    user_count=500000,
    scraping_method="public_api",
    rate_limit_per_minute=10,
    is_active=True
)
```

## Triggering Scraping

### Method 1: Via API (Recommended)

#### Scrape a Specific Platform

```bash
POST /api/scrapers/jobs/scrape_platform/
Content-Type: application/json
Authorization: Bearer <your-token>

{
  "platform_id": 1,
  "limit": 50
}
```

Response:
```json
{
  "status": "started",
  "platform": "Stack Overflow Jobs",
  "task_id": "abc123-def456-..."
}
```

#### Scrape All Active Platforms

```bash
POST /api/scrapers/jobs/scrape_all/
Content-Type: application/json
Authorization: Bearer <your-token>

{
  "limit": 50
}
```

### Method 2: Via Django Shell

```python
python manage.py shell

from scrapers.tasks import scrape_platform, scrape_all_active_platforms

# Scrape specific platform
result = scrape_platform.delay(platform_id=1, limit=50)

# Scrape all active platforms
result = scrape_all_active_platforms.delay(limit=50)
```

### Method 3: Via Management Command (Synchronous)

Create a custom management command or use Django shell:

```python
python manage.py shell

from scrapers.scrapers import get_scraper
from projects.models import SourcePlatform

platform = SourcePlatform.objects.get(id=1)
scraper = get_scraper(platform)
projects = scraper.scrape(limit=10)

# Process projects manually
for project_data in projects:
    print(f"Found: {project_data.get('title')}")
```

### Method 4: Scheduled Scraping (Celery Beat)

Scraping is automatically scheduled if Celery Beat is running:

- **Daily**: Runs at 2 AM (50 projects per platform)
- **Hourly**: Runs every hour (20 projects per platform)

To start Celery Beat:
```bash
cd timothy-llc/backend
celery -A project_matcher beat -l info
```

## Scraping Methods

### 1. RSS Feed Scraping

Best for: Job boards with RSS feeds (Stack Overflow, We Work Remotely, etc.)

**Setup:**
```python
platform = SourcePlatform.objects.create(
    name="Stack Overflow Jobs",
    url="https://stackoverflow.com/jobs/feed",
    scraping_method="rss_feed",
    rate_limit_per_minute=10
)
```

**How it works:**
- Fetches RSS/Atom feed
- Parses `<item>` elements
- Extracts: title, description, link
- Automatically handles rate limiting

### 2. Public API Scraping

Best for: Platforms with public APIs (RemoteOK, GitHub Jobs, etc.)

**Setup:**
```python
platform = SourcePlatform.objects.create(
    name="RemoteOK API",
    url="https://remoteok.com/json",
    scraping_method="public_api",
    rate_limit_per_minute=10
)
```

**Note:** The built-in `APIScraper` parses RemoteOK-style JSON. Other APIs that return a list of job objects with `position`/`title`, `description`, `url` are supported; add custom logic in `_parse_api_response()` for other formats.

### 3. Public HTML Scraping

Best for: Public job listings (use carefully, respect ToS)

**Setup:**
```python
platform = SourcePlatform.objects.create(
    name="Job Board",
    url="https://example.com/jobs",
    scraping_method="public_scrape",
    rate_limit_per_minute=5  # Lower rate for HTML scraping
)
```

**Note:** You need to implement custom parsing in `JobBoardScraper` class.

## Creating Custom Scrapers

### Example: Custom RSS Scraper with Enhanced Parsing

Edit `timothy-llc/backend/scrapers/scrapers.py`:

```python
class EnhancedRSSScraper(RSSFeedScraper):
    """Enhanced RSS scraper with better parsing."""
    
    def _parse_rss_item(self, item) -> Optional[Dict]:
        """Parse RSS item with additional fields."""
        try:
            title = item.find('title')
            description = item.find('description')
            link = item.find('link')
            
            if not title or not link:
                return None
            
            # Extract additional data
            company = item.find('company') or item.find('dc:creator')
            budget = item.find('budget') or item.find('salary')
            skills = []
            
            # Parse skills from description or tags
            tags = item.find_all('category')
            for tag in tags:
                skills.append(tag.get_text().strip())
            
            return {
                'title': title.get_text().strip(),
                'description': description.get_text().strip() if description else '',
                'source_url': link.get_text().strip(),
                'source_id': link.get_text().strip().split('/')[-1],
                'company_name': company.get_text().strip() if company else None,
                'budget_min': self._parse_budget(budget) if budget else None,
                'skills_required': skills,
            }
        except Exception as e:
            logger.error(f"Error parsing RSS item: {e}")
            return None
    
    def _parse_budget(self, budget_element):
        """Parse budget from various formats."""
        # Implement your budget parsing logic
        return None
```

### Example: Custom API Scraper

```python
class RemoteOKScraper(APIScraper):
    """Custom scraper for RemoteOK API."""
    
    def _parse_api_response(self, data: Dict) -> List[Dict]:
        """Parse RemoteOK API response."""
        projects = []
        
        # RemoteOK returns a list of job objects
        for job in data:
            projects.append({
                'title': job.get('title', ''),
                'description': job.get('description', ''),
                'source_url': f"https://remoteok.com/remote-jobs/{job.get('id')}",
                'source_id': str(job.get('id', '')),
                'company_name': job.get('company', ''),
                'budget_min': job.get('salary_min'),
                'budget_max': job.get('salary_max'),
                'skills_required': job.get('tags', []),
                'contact_email': job.get('email'),
            })
        
        return projects
```

Then update `get_scraper()` function:

```python
def get_scraper(platform) -> BaseScraper:
    """Factory function to get appropriate scraper for platform."""
    scraping_method = platform.scraping_method
    
    if scraping_method == 'rss_feed':
        if 'stackoverflow' in platform.url.lower():
            return EnhancedRSSScraper(platform, rate_limit_delay=60/platform.rate_limit_per_minute)
        return RSSFeedScraper(platform, rate_limit_delay=60/platform.rate_limit_per_minute)
    elif scraping_method == 'public_api':
        if 'remoteok' in platform.url.lower():
            return RemoteOKScraper(platform, rate_limit_delay=60/platform.rate_limit_per_minute)
        return APIScraper(platform, rate_limit_delay=60/platform.rate_limit_per_minute)
    # ... rest of the function
```

## Testing Scraping

### Test RSS Feed Scraping

```python
python manage.py shell

from projects.models import SourcePlatform
from scrapers.scrapers import get_scraper

# Create test platform
platform = SourcePlatform.objects.create(
    name="Test RSS Feed",
    url="https://stackoverflow.com/jobs/feed",  # Example RSS feed
    scraping_method="rss_feed",
    rate_limit_per_minute=10
)

# Test scraper
scraper = get_scraper(platform)
projects = scraper.scrape(limit=5)

# Check results
for project in projects:
    print(f"Title: {project.get('title')}")
    print(f"URL: {project.get('source_url')}")
    print("---")
```

### Test API Scraping

```python
python manage.py shell

from projects.models import SourcePlatform
from scrapers.scrapers import get_scraper
import requests

# Test API endpoint first
url = "https://remoteok.com/api"
response = requests.get(url)
print(response.json()[:1])  # Print first item to see structure

# Then create platform and test
platform = SourcePlatform.objects.create(
    name="Test API",
    url=url,
    scraping_method="public_api",
    rate_limit_per_minute=10
)

scraper = get_scraper(platform)
projects = scraper.scrape(limit=5)
```

### Test Full Scraping Pipeline

```python
python manage.py shell

from scrapers.tasks import scrape_platform
from projects.models import SourcePlatform

platform = SourcePlatform.objects.get(id=1)
result = scrape_platform.delay(platform.id, limit=10)

# Check result (after task completes)
print(result.get())  # Returns: {'status': 'success', 'projects_added': 5}
```

## Viewing Scraping Results

### Via Django Admin

1. Go to `http://localhost:8000/admin`
2. **Scrapers → Scraping Jobs**: View all scraping jobs and their status
3. **Projects → Project Leads**: View scraped projects

### Via API

```bash
# Get scraping jobs
GET /api/scrapers/jobs/

# Get scraped projects
GET /api/projects/leads/
```

## Troubleshooting

### Issue: No projects found

**Possible causes:**
1. RSS feed URL is incorrect
2. API endpoint requires authentication
3. HTML structure changed
4. Rate limiting too aggressive

**Solutions:**
- Test the URL manually (browser/curl)
- Check scraping job error messages in admin
- Adjust rate_limit_per_minute
- Review scraper logs

### Issue: Scraping job fails

**Check:**
1. Django logs: `python manage.py runserver` (check console)
2. Celery logs: Check Celery worker output
3. Scraping job error: Admin → Scraping Jobs → View error_message

### Issue: 404 or 403 errors

**404 Not Found (e.g. TechJobs Pro, custom API):**
- The platform URL may be wrong or the API may not exist. Sample data uses placeholder URLs; for a working API use `https://remoteok.com/json` and scraping method `public_api`.
- In Django Admin → Projects → Source Platforms, edit the platform and set **URL** to a real endpoint (e.g. `https://remoteok.com/json` for the first sample platform).

**403 Forbidden (e.g. Stack Overflow Jobs RSS):**
- Some feeds (Stack Overflow Jobs, Indeed-powered feeds) use Cloudflare or bot detection and may block server/script requests. The scraper uses browser-like headers to reduce this; if 403 persists:
  - Try from a different network (some hosts are blocked).
  - Consider using a different RSS source (e.g. We Work Remotely: `https://weworkremotely.com/categories/remote-programming-jobs.rss`).
  - Stack Overflow Jobs may require using their official API or accepting that the RSS feed is not always accessible to automation.

### Issue: Duplicate projects

The system automatically prevents duplicates by checking `source_url`. If you see duplicates:
- Check if URLs are slightly different
- Verify `source_url` is being set correctly in scraper

### Issue: Projects not qualified

**Check:**
- Are projects being created? (Admin → Project Leads)
- Check `relevance_score` and `quality_score` values
- Review qualification logic in `scrapers/qualifiers.py`

## Best Practices

1. **Respect Rate Limits**: Always set appropriate `rate_limit_per_minute`
2. **Check Terms of Service**: Only scrape publicly available data
3. **Handle Errors Gracefully**: Scrapers should log errors, not crash
4. **Test First**: Test scrapers manually before scheduling
5. **Monitor Jobs**: Regularly check scraping job status
6. **Update Scrapers**: When source sites change, update scrapers accordingly

## Example: Complete Scraping Workflow

```python
# 1. Create platform
from projects.models import SourcePlatform
platform = SourcePlatform.objects.create(
    name="Example Jobs",
    url="https://example.com/jobs/feed",
    scraping_method="rss_feed",
    rate_limit_per_minute=10,
    is_active=True
)

# 2. Test scraper
from scrapers.scrapers import get_scraper
scraper = get_scraper(platform)
test_projects = scraper.scrape(limit=5)
print(f"Test found {len(test_projects)} projects")

# 3. Run full scraping (via Celery)
from scrapers.tasks import scrape_platform
result = scrape_platform.delay(platform.id, limit=50)

# 4. Check results
print(f"Task ID: {result.id}")
# Wait for completion, then:
print(result.get())  # {'status': 'success', 'projects_added': 45}

# 5. View projects
from projects.models import ProjectLead
projects = ProjectLead.objects.filter(source_platform=platform)
print(f"Total projects: {projects.count()}")
```

## Next Steps

- Set up Celery for background scraping
- Configure scheduled scraping (Celery Beat)
- Create custom scrapers for your target platforms
- Monitor scraping jobs regularly
- Adjust qualification rules as needed
