# Quick Scraping Test Guide

## Problem: No Source Platforms in Database

If you get `SourcePlatform.DoesNotExist`, you need to create platforms first.

## Solution 1: Create Sample Data (Recommended)

This creates platforms AND sample projects:

```bash
cd timothy-llc/backend
python manage.py create_sample_data
```

This will create:
- 3 sample source platforms
- 12 sample projects
- System settings

## Solution 2: Create Platform Manually

### Via Django Shell

```python
python manage.py shell

from projects.models import SourcePlatform

# Create a test RSS feed platform
platform = SourcePlatform.objects.create(
    name="Stack Overflow Jobs",
    url="https://stackoverflow.com/jobs/feed",
    user_count=2000000,
    scraping_method="rss_feed",
    rate_limit_per_minute=10,
    is_active=True
)

print(f"Created platform: {platform.id} - {platform.name}")
```

### Via Django Admin

1. Go to `http://localhost:8000/admin`
2. Navigate to **Projects → Source Platforms**
3. Click **Add Source Platform**
4. Fill in the form and save

## Solution 3: Test Scraping (After Platform Exists)

### Option A: Test Scraper Directly (Synchronous)

```python
python manage.py shell

from projects.models import SourcePlatform
from scrapers.scrapers import get_scraper

# Get platform
platform = SourcePlatform.objects.first()  # or .get(id=1)
print(f"Testing: {platform.name}")

# Get scraper
scraper = get_scraper(platform)

# Test scraping (synchronous - will take time)
projects = scraper.scrape(limit=5)

# Check results
print(f"Found {len(projects)} projects:")
for project in projects:
    print(f"  - {project.get('title')}")
```

### Option B: Use Celery Task (Asynchronous)

**First, make sure Celery is running:**

```bash
# Terminal 1: Start Redis (if not running)
redis-server

# Terminal 2: Start Celery worker
cd timothy-llc/backend
celery -A project_matcher worker -l info
```

**Then in Django shell:**

```python
python manage.py shell

from scrapers.tasks import scrape_platform
from projects.models import SourcePlatform

platform = SourcePlatform.objects.first()
result = scrape_platform.delay(platform.id, limit=10)

print(f"Task ID: {result.id}")
print("Check Celery worker terminal for progress")
print("Or wait and check result:")
print(result.get())  # This will wait for completion
```

### Option C: Use Management Command

```bash
python manage.py test_scraper <platform_id> --limit 5
```

## Quick Start: Full Example

```python
python manage.py shell

# Step 1: Create platform
from projects.models import SourcePlatform
platform = SourcePlatform.objects.create(
    name="Test RSS Feed",
    url="https://stackoverflow.com/jobs/feed",
    scraping_method="rss_feed",
    rate_limit_per_minute=10,
    is_active=True
)

# Step 2: Test scraper
from scrapers.scrapers import get_scraper
scraper = get_scraper(platform)
projects = scraper.scrape(limit=3)

# Step 3: Check results
for project in projects:
    print(f"Title: {project.get('title')}")
    print(f"URL: {project.get('source_url')}")
    print("---")
```

## Common Issues

### Issue: "SourcePlatform matching query does not exist"

**Solution:** Create a platform first (see Solution 1 or 2 above)

### Issue: "scrape_platform is not defined"

**Solution:** Import it first:
```python
from scrapers.tasks import scrape_platform
```

### Issue: Scraper returns empty list

**Possible causes:**
- RSS feed URL is incorrect
- Feed is empty
- Network issues
- Rate limiting

**Solution:**
- Test the URL in browser first
- Check scraper logs
- Try a different platform/URL

### Issue: Celery task not running

**Solution:**
- Make sure Redis is running
- Make sure Celery worker is running
- Check Celery worker logs for errors

## Recommended Workflow

1. **Create sample data:**
   ```bash
   python manage.py create_sample_data
   ```

2. **Test a scraper:**
   ```bash
   python manage.py test_scraper 1 --limit 5
   ```

3. **Run full scraping (if Celery is set up):**
   ```python
   from scrapers.tasks import scrape_platform
   scrape_platform.delay(1, limit=50)
   ```

4. **Check results in Django admin:**
   - Go to `http://localhost:8000/admin`
   - Check **Projects → Project Leads**
   - Check **Scrapers → Scraping Jobs**
