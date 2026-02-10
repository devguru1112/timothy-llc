"""
Quick script to create a test platform and test scraping.
Run with: python manage.py shell < quick_test_scraping.py
Or copy-paste into Django shell.
"""

from projects.models import SourcePlatform
from scrapers.scrapers import get_scraper

# Create a test platform
platform, created = SourcePlatform.objects.get_or_create(
    name="Stack Overflow Jobs",
    defaults={
        'url': 'https://stackoverflow.com/jobs/feed',
        'user_count': 2000000,
        'scraping_method': 'rss_feed',
        'rate_limit_per_minute': 10,
        'is_active': True,
    }
)

if created:
    print(f"✓ Created platform: {platform.id} - {platform.name}")
else:
    print(f"✓ Platform already exists: {platform.id} - {platform.name}")

# Test the scraper
print(f"\nTesting scraper for: {platform.name}")
print(f"URL: {platform.url}")
print(f"Method: {platform.scraping_method}")
print("-" * 50)

try:
    scraper = get_scraper(platform)
    print("Scraper created successfully")
    print("Scraping projects (this may take a moment)...")
    
    projects = scraper.scrape(limit=5)
    
    if not projects:
        print("\n⚠ No projects found. This could mean:")
        print("  - RSS feed is empty")
        print("  - URL is incorrect")
        print("  - Network issue")
        print("\nTry testing the URL in your browser first.")
    else:
        print(f"\n✓ Found {len(projects)} projects:\n")
        for i, project in enumerate(projects, 1):
            print(f"{i}. {project.get('title', 'No title')}")
            print(f"   URL: {project.get('source_url', 'No URL')}")
            if project.get('description'):
                desc = project.get('description', '')[:100]
                print(f"   Description: {desc}...")
            print()
        
        print(f"\n✓ Successfully scraped {len(projects)} projects!")
        print("\nTo save these to database, use:")
        print("  from scrapers.tasks import scrape_platform")
        print(f"  scrape_platform.delay({platform.id}, limit=50)")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
