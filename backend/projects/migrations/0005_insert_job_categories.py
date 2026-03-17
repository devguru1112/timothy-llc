# Data migration: insert default job categories (SEO, Marketing, Social Media, etc.)

from django.db import migrations

JOB_CATEGORIES = [
    {
        "name": "SEO",
        "keywords": [
            "SEO",
            "search engine optimization",
            "keyword research",
            "organic traffic",
            "backlinks",
            "on-page SEO",
            "technical SEO",
        ],
    },
    {
        "name": "Marketing",
        "keywords": [
            "marketing",
            "digital marketing",
            "campaign",
            "brand",
            "growth",
            "conversion",
            "lead generation",
            "content marketing",
        ],
    },
    {
        "name": "Social Media",
        "keywords": [
            "social media",
            "Facebook",
            "Instagram",
            "Twitter",
            "TikTok",
            "LinkedIn",
            "social strategy",
            "community management",
            "engagement",
        ],
    },
    {
        "name": "Website Design",
        "keywords": [
            "website design",
            "web design",
            "UI",
            "UX",
            "wireframe",
            "landing page",
            "WordPress",
            "responsive design",
            "front-end",
        ],
    },
    {
        "name": "LinkedIn Management",
        "keywords": [
            "LinkedIn",
            "LinkedIn management",
            "LinkedIn strategy",
            "LinkedIn marketing",
            "LinkedIn profile",
            "B2B LinkedIn",
            "LinkedIn outreach",
        ],
    },
]


def insert_job_categories(apps, schema_editor):
    JobCategory = apps.get_model("projects", "JobCategory")
    for data in JOB_CATEGORIES:
        JobCategory.objects.update_or_create(
            name=data["name"],
            defaults={"keywords": data["keywords"], "is_active": True},
        )


def reverse_insert_job_categories(apps, schema_editor):
    JobCategory = apps.get_model("projects", "JobCategory")
    for data in JOB_CATEGORIES:
        JobCategory.objects.filter(name=data["name"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0004_insert_scraping_source_platforms"),
    ]

    operations = [
        migrations.RunPython(insert_job_categories, reverse_insert_job_categories),
    ]
