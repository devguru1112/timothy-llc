# Data migration: insert RemoteOK, USAJobs, ITJobPro as source platforms for scraping

from django.db import migrations


SCRAPING_PLATFORMS = [
    {
        "name": "RemoteOK",
        "url": "https://remoteok.com/api",
        "user_count": 500000,
        "scraping_method": "public_api",
        "rate_limit_per_minute": 10,
        "is_active": True,
    },
    {
        "name": "USAJobs",
        "url": "https://data.usajobs.gov/api/search",
        "user_count": 2000000,
        "scraping_method": "public_api",
        "rate_limit_per_minute": 10,
        "is_active": True,
    },
    {
        "name": "ITJobPro",
        "url": "https://itjobpro.com/jobs/",
        "user_count": 100000,
        "scraping_method": "public_scrape",
        "rate_limit_per_minute": 5,
        "is_active": True,
    },
]


def insert_scraping_platforms(apps, schema_editor):
    SourcePlatform = apps.get_model("projects", "SourcePlatform")
    for data in SCRAPING_PLATFORMS:
        SourcePlatform.objects.update_or_create(
            name=data["name"],
            defaults={
                "url": data["url"],
                "user_count": data["user_count"],
                "scraping_method": data["scraping_method"],
                "rate_limit_per_minute": data["rate_limit_per_minute"],
                "is_active": data["is_active"],
            },
        )


def noop_reverse(apps, schema_editor):
    # Optional: remove only these three by name if you want to reverse
    SourcePlatform = apps.get_model("projects", "SourcePlatform")
    for data in SCRAPING_PLATFORMS:
        SourcePlatform.objects.filter(name=data["name"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0003_jobcategory_scrapingconfig_projectlead_categories"),
    ]

    operations = [
        migrations.RunPython(insert_scraping_platforms, noop_reverse),
    ]
