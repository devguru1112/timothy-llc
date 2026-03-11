# Data migration: run setup_initial_settings (create default SystemSettings if missing)

from django.db import migrations

INITIAL_SETTINGS = [
    {
        "key": "free_projects_limit",
        "value": "10",
        "description": "Number of free projects shown to non-authenticated users",
    },
    {
        "key": "free_applications_limit",
        "value": "3",
        "description": "Number of free applications allowed before requiring registration",
    },
    {
        "key": "usajobs_api_key",
        "value": "",
        "description": "USAJobs.gov API Authorization-Key (required for USAJobs scraper). Get one at https://www.usajobs.gov/Help/working-in-government/unique-hiring-paths/students/federal-internships/",
    },
    {
        "key": "usajobs_user_email",
        "value": "",
        "description": "Email used as User-Agent for USAJobs.gov API (required for USAJobs scraper).",
    },
]


def run_setup_initial_settings(apps, schema_editor):
    SystemSettings = apps.get_model("projects", "SystemSettings")
    for data in INITIAL_SETTINGS:
        SystemSettings.objects.get_or_create(
            key=data["key"],
            defaults={
                "value": data["value"],
                "description": data["description"],
            },
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0005_insert_job_categories"),
    ]

    operations = [
        migrations.RunPython(run_setup_initial_settings, noop_reverse),
    ]
