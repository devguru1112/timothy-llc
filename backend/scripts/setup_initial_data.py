"""
Script to set up initial data for the project matcher.
Run with: python manage.py shell < scripts/setup_initial_data.py
Or: python manage.py runscript setup_initial_data
"""
from projects.models import SourcePlatform
from outreach.models import OutreachTemplate
from django.contrib.auth import get_user_model

User = get_user_model()


def setup_source_platforms():
    """Create initial source platforms."""
    platforms = [
        {
            'name': 'RemoteOK',
            'url': 'https://remoteok.com/json',
            'user_count': 500000,
            'scraping_method': 'public_api',
            'rate_limit_per_minute': 10,
            'is_active': True,
        },
        {
            'name': 'We Work Remotely',
            'url': 'https://weworkremotely.com/categories/remote-programming-jobs.rss',
            'user_count': 300000,
            'scraping_method': 'rss_feed',
            'rate_limit_per_minute': 5,
            'is_active': True,
        },
        {
            'name': 'AngelList Jobs',
            'url': 'https://angel.co/jobs',
            'user_count': 1000000,
            'scraping_method': 'public_scrape',
            'rate_limit_per_minute': 10,
            'is_active': True,
        },
        {
            'name': 'Stack Overflow Jobs',
            'url': 'https://stackoverflow.com/jobs/feed',
            'user_count': 2000000,
            'scraping_method': 'rss_feed',
            'rate_limit_per_minute': 10,
            'is_active': True,
        },
    ]
    
    created_count = 0
    for platform_data in platforms:
        platform, created = SourcePlatform.objects.get_or_create(
            name=platform_data['name'],
            defaults=platform_data
        )
        if created:
            created_count += 1
            print(f"Created platform: {platform.name}")
        else:
            print(f"Platform already exists: {platform.name}")
    
    print(f"\nCreated {created_count} new platforms")
    return created_count


def setup_outreach_templates():
    """Create default outreach email templates."""
    templates = [
        {
            'name': 'Default Outreach',
            'subject': 'Quick question about your {project_title} project',
            'body': '''Hi {recipient_name},

I came across your project "{project_title}" and wanted to reach out to see if you're still looking for help.

I'm {user_name}, and I specialize in the technologies you mentioned. I'd love to learn more about your project and see if I can help bring it to life.

You can check out my work at: {portfolio_url}
Or reach me directly at: {user_email}

Looking forward to hearing from you!

Best regards,
{user_name}''',
            'is_default': True,
        },
        {
            'name': 'Follow-up Template',
            'subject': 'Following up on {project_title}',
            'body': '''Hi {recipient_name},

I wanted to follow up on my previous message about your "{project_title}" project.

I'm still very interested in helping with this project and would love to discuss how I can contribute. I have experience with the technologies you're looking for and can provide references if needed.

Feel free to reach out at {user_email} or check out my portfolio: {portfolio_url}

Best regards,
{user_name}''',
            'is_default': False,
        },
    ]
    
    created_count = 0
    for template_data in templates:
        template, created = OutreachTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )
        if created:
            created_count += 1
            print(f"Created template: {template.name}")
        else:
            print(f"Template already exists: {template.name}")
    
    print(f"\nCreated {created_count} new templates")
    return created_count


def run_setup():
    """Run all setup functions."""
    print("Setting up initial data...\n")
    setup_source_platforms()
    print("\n" + "="*50 + "\n")
    setup_outreach_templates()
    print("\n" + "="*50)
    print("\nSetup complete!")


if __name__ == '__main__':
    run_setup()
