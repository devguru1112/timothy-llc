"""
Django management command to create sample projects and data for frontend demo.

Usage:
    python manage.py create_sample_data
"""
from django.core.management.base import BaseCommand
from projects.models import SourcePlatform, ProjectLead, SystemSettings
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Creates sample projects and data for frontend demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sample data before creating new',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing sample data...')
            # Clear projects from sample platforms
            sample_platform_names = [
                'TechJobs Pro', 'Remote Work Hub', 'Freelance Marketplace'
            ]
            ProjectLead.objects.filter(source_platform__name__in=sample_platform_names).delete()
            SourcePlatform.objects.filter(name__in=sample_platform_names).delete()

        self.stdout.write('Creating sample data...')

        # Create sample source platforms
        platforms = self.create_platforms()
        
        # Create sample projects
        projects = self.create_projects(platforms)
        
        # Set up system settings
        self.setup_settings()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(platforms)} platforms and {len(projects)} sample projects!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                'All projects are marked as public and ready to view at /public'
            )
        )

    def create_platforms(self):
        """Create sample source platforms."""
        platforms_data = [
            {
                'name': 'TechJobs Pro',
                'url': 'https://techjobspro.com/api',
                'user_count': 250000,
                'scraping_method': 'public_api',
                'is_active': True,
            },
            {
                'name': 'Remote Work Hub',
                'url': 'https://remoteworkhub.com/feed',
                'user_count': 180000,
                'scraping_method': 'rss_feed',
                'is_active': True,
            },
            {
                'name': 'Freelance Marketplace',
                'url': 'https://freelancemarketplace.com',
                'user_count': 500000,
                'scraping_method': 'public_scrape',
                'is_active': True,
            },
        ]

        platforms = []
        for data in platforms_data:
            platform, created = SourcePlatform.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            platforms.append(platform)
            if created:
                self.stdout.write(f'  Created platform: {platform.name}')
            else:
                self.stdout.write(f'  Platform already exists: {platform.name}')

        return platforms

    def create_projects(self, platforms):
        """Create sample projects."""
        projects_data = [
            {
                'title': 'Full-Stack Web Application Development',
                'description': '''We're looking for an experienced full-stack developer to build a modern web application using React and Django. The project involves creating a user dashboard, payment integration, and real-time notifications.

Requirements:
- 3+ years experience with React and Django
- Experience with PostgreSQL
- Knowledge of RESTful APIs
- Experience with payment gateways (Stripe preferred)

The project is expected to take 3-4 months with flexible working hours. We offer competitive rates and the opportunity to work on an exciting product.''',
                'company_name': 'TechStart Inc.',
                'budget_min': 15000,
                'budget_max': 25000,
                'budget_currency': 'USD',
                'skills_required': ['React', 'Django', 'PostgreSQL', 'REST API', 'Stripe'],
                'project_type': 'Web Development',
                'relevance_score': 0.92,
                'quality_score': 0.88,
                'status': 'qualified',
            },
            {
                'title': 'E-commerce Platform with React and Node.js',
                'description': '''Looking for a skilled developer to build a complete e-commerce platform. The application needs to handle product catalog, shopping cart, user authentication, and order management.

Key features:
- Product search and filtering
- Shopping cart functionality
- User accounts and profiles
- Payment processing
- Admin dashboard

We need someone who can work independently and deliver high-quality code. Experience with e-commerce platforms is a plus.''',
                'company_name': 'ShopSmart Solutions',
                'budget_min': 20000,
                'budget_max': 35000,
                'budget_currency': 'USD',
                'skills_required': ['React', 'Node.js', 'MongoDB', 'Express', 'Payment Integration'],
                'project_type': 'E-commerce',
                'relevance_score': 0.85,
                'quality_score': 0.82,
                'status': 'qualified',
            },
            {
                'title': 'Mobile App Development - iOS & Android',
                'description': '''We need a mobile app developer to create a cross-platform mobile application for our fitness tracking service. The app should sync with our backend API and provide real-time workout tracking.

Features needed:
- User authentication
- Workout tracking and logging
- Progress charts and analytics
- Social features (sharing workouts)
- Push notifications

Preference for React Native or Flutter developers. Must have experience publishing apps to App Store and Google Play.''',
                'company_name': 'FitLife Technologies',
                'budget_min': 18000,
                'budget_max': 30000,
                'budget_currency': 'USD',
                'skills_required': ['React Native', 'Flutter', 'Mobile Development', 'iOS', 'Android'],
                'project_type': 'Mobile Development',
                'relevance_score': 0.78,
                'quality_score': 0.80,
                'status': 'qualified',
            },
            {
                'title': 'Python Backend API Development',
                'description': '''Seeking an experienced Python developer to build a robust REST API backend for our SaaS platform. The API will handle user management, data processing, and third-party integrations.

Technical requirements:
- Python 3.9+
- Django REST Framework
- PostgreSQL database
- Redis for caching
- Experience with Celery for background tasks
- API documentation (OpenAPI/Swagger)

The project timeline is 2-3 months. We're looking for clean, maintainable code following best practices.''',
                'company_name': 'CloudScale Systems',
                'budget_min': 12000,
                'budget_max': 20000,
                'budget_currency': 'USD',
                'skills_required': ['Python', 'Django', 'PostgreSQL', 'Redis', 'Celery', 'REST API'],
                'project_type': 'Backend Development',
                'relevance_score': 0.90,
                'quality_score': 0.85,
                'status': 'qualified',
            },
            {
                'title': 'Frontend Developer - React Dashboard',
                'description': '''We need a frontend developer to create a beautiful and intuitive admin dashboard using React. The dashboard will display analytics, user management, and system configuration.

Design requirements:
- Modern, clean UI design
- Responsive layout (mobile-friendly)
- Data visualization (charts and graphs)
- Real-time updates
- Dark mode support

You'll be working with our design team and backend developers. Experience with TailwindCSS and Chart.js is preferred.''',
                'company_name': 'DataViz Analytics',
                'budget_min': 8000,
                'budget_max': 15000,
                'budget_currency': 'USD',
                'skills_required': ['React', 'TailwindCSS', 'JavaScript', 'Chart.js', 'Responsive Design'],
                'project_type': 'Frontend Development',
                'relevance_score': 0.88,
                'quality_score': 0.83,
                'status': 'qualified',
            },
            {
                'title': 'WordPress to Custom Platform Migration',
                'description': '''Looking for a developer to migrate our WordPress website to a custom-built platform using modern technologies. The new platform needs to maintain all existing functionality while improving performance and user experience.

Migration tasks:
- Content migration
- User data migration
- Custom functionality replication
- SEO preservation
- Performance optimization

Experience with WordPress and modern web frameworks required. Timeline: 4-6 weeks.''',
                'company_name': 'Digital Transform Co.',
                'budget_min': 10000,
                'budget_max': 18000,
                'budget_currency': 'USD',
                'skills_required': ['WordPress', 'PHP', 'React', 'Migration', 'SEO'],
                'project_type': 'Website Migration',
                'relevance_score': 0.75,
                'quality_score': 0.77,
                'status': 'qualified',
            },
            {
                'title': 'Blockchain Integration Developer',
                'description': '''We're building a decentralized application and need a developer with blockchain experience to integrate smart contracts and Web3 functionality.

Requirements:
- Solidity programming
- Ethereum/Web3.js
- Smart contract development
- Testing and deployment
- Security best practices

This is a long-term project with potential for ongoing work. Must have proven experience with blockchain development.''',
                'company_name': 'CryptoInnovate Labs',
                'budget_min': 25000,
                'budget_max': 40000,
                'budget_currency': 'USD',
                'skills_required': ['Solidity', 'Blockchain', 'Web3', 'Ethereum', 'Smart Contracts'],
                'project_type': 'Blockchain Development',
                'relevance_score': 0.82,
                'quality_score': 0.79,
                'status': 'qualified',
            },
            {
                'title': 'DevOps Engineer - CI/CD Pipeline Setup',
                'description': '''Need a DevOps engineer to set up and optimize our CI/CD pipeline. The infrastructure includes Docker containers, AWS services, and automated testing.

Tasks:
- Set up CI/CD with GitHub Actions or GitLab CI
- Docker containerization
- AWS deployment automation
- Monitoring and logging setup
- Security scanning integration

Looking for someone who can document the process and train our team. Experience with Terraform is a plus.''',
                'company_name': 'InfraTech Solutions',
                'budget_min': 15000,
                'budget_max': 25000,
                'budget_currency': 'USD',
                'skills_required': ['DevOps', 'CI/CD', 'Docker', 'AWS', 'GitHub Actions', 'Terraform'],
                'project_type': 'DevOps',
                'relevance_score': 0.80,
                'quality_score': 0.81,
                'status': 'qualified',
            },
            {
                'title': 'UI/UX Designer + Frontend Developer',
                'description': '''We're looking for a talented designer-developer hybrid to create a beautiful user interface for our new product. You'll be responsible for both design and implementation.

What we need:
- UI/UX design (Figma/Sketch)
- Frontend development (React)
- Design system creation
- User research and testing
- Responsive design implementation

This is a 3-month project with the possibility of extension. Portfolio showcasing both design and development skills is required.''',
                'company_name': 'Creative Digital Agency',
                'budget_min': 14000,
                'budget_max': 22000,
                'budget_currency': 'USD',
                'skills_required': ['UI/UX Design', 'Figma', 'React', 'Design Systems', 'User Research'],
                'project_type': 'Design & Development',
                'relevance_score': 0.87,
                'quality_score': 0.84,
                'status': 'qualified',
            },
            {
                'title': 'Machine Learning Model Development',
                'description': '''Seeking a data scientist/ML engineer to develop a recommendation system for our platform. The model should analyze user behavior and provide personalized recommendations.

Project scope:
- Data analysis and preprocessing
- Model development and training
- API integration
- Performance optimization
- Documentation

Experience with Python, TensorFlow/PyTorch, and recommendation systems required. Access to our dataset will be provided.''',
                'company_name': 'AI Solutions Corp',
                'budget_min': 20000,
                'budget_max': 35000,
                'budget_currency': 'USD',
                'skills_required': ['Machine Learning', 'Python', 'TensorFlow', 'Data Science', 'Recommendation Systems'],
                'project_type': 'Machine Learning',
                'relevance_score': 0.79,
                'quality_score': 0.76,
                'status': 'qualified',
            },
            {
                'title': 'API Integration Specialist',
                'description': '''We need a developer to integrate multiple third-party APIs into our platform. The integrations include payment processing, email services, and analytics tools.

Integrations needed:
- Stripe payment gateway
- SendGrid email service
- Google Analytics
- Twilio SMS service
- AWS S3 storage

Must have experience with API integration, error handling, and webhook management. Good documentation skills are essential.''',
                'company_name': 'Integration Experts LLC',
                'budget_min': 6000,
                'budget_max': 12000,
                'budget_currency': 'USD',
                'skills_required': ['API Integration', 'REST API', 'Webhooks', 'Payment Processing', 'Third-party APIs'],
                'project_type': 'API Integration',
                'relevance_score': 0.83,
                'quality_score': 0.80,
                'status': 'qualified',
            },
            {
                'title': 'Database Optimization & Migration',
                'description': '''Our application is experiencing performance issues with the database. We need an expert to optimize queries, improve indexing, and potentially migrate to a more scalable solution.

Tasks:
- Query optimization
- Database schema review
- Index optimization
- Migration planning (if needed)
- Performance monitoring setup

Current stack: PostgreSQL. Experience with large-scale databases and performance tuning is required.''',
                'company_name': 'DataFlow Systems',
                'budget_min': 10000,
                'budget_max': 18000,
                'budget_currency': 'USD',
                'skills_required': ['PostgreSQL', 'Database Optimization', 'SQL', 'Performance Tuning', 'Migration'],
                'project_type': 'Database',
                'relevance_score': 0.76,
                'quality_score': 0.78,
                'status': 'qualified',
            },
        ]

        projects = []
        base_time = timezone.now() - timedelta(days=30)

        for i, data in enumerate(projects_data):
            # Distribute projects across platforms
            platform = platforms[i % len(platforms)]
            
            # Create unique source URL
            source_url = f'https://{platform.name.lower().replace(" ", "")}.com/projects/{i+1}'
            
            # Check if project already exists
            if ProjectLead.objects.filter(source_url=source_url).exists():
                self.stdout.write(f'  Project already exists: {data["title"]}')
                continue

            project = ProjectLead.objects.create(
                title=data['title'],
                description=data['description'],
                source_platform=platform,
                source_url=source_url,
                source_id=str(i + 1),
                company_name=data['company_name'],
                budget_min=data['budget_min'],
                budget_max=data['budget_max'],
                budget_currency=data['budget_currency'],
                skills_required=data['skills_required'],
                project_type=data['project_type'],
                relevance_score=data['relevance_score'],
                quality_score=data['quality_score'],
                status=data['status'],
                is_public=True,  # All sample projects are public
                scraped_at=base_time + timedelta(days=random.randint(0, 30)),
                qualified_at=base_time + timedelta(days=random.randint(0, 25)),
            )

            projects.append(project)
            self.stdout.write(f'  Created project: {project.title}')

        return projects

    def setup_settings(self):
        """Set up system settings if they don't exist."""
        setting, created = SystemSettings.objects.get_or_create(
            key='free_projects_limit',
            defaults={
                'value': '12',
                'description': 'Number of free projects shown to non-authenticated users',
            }
        )
        if created:
            self.stdout.write(f'  Created setting: free_projects_limit = {setting.value}')
        else:
            self.stdout.write(f'  Setting already exists: free_projects_limit = {setting.value}')
