# Project Matcher - Timothy Morgan LLC

An agentic project aggregation and matching platform that helps community members discover and connect with relevant project opportunities.

## Features

- **Compliant Scraping**: Aggregates projects from publicly available sources (RSS feeds, public APIs, job boards)
- **AI-Powered Qualification**: Automatically scores projects for relevance and quality
- **Smart Matching**: Matches projects with community members based on skills and priority
- **Outreach Management**: Track and manage outreach messages to prospects
- **User Dashboard**: View available projects, matched projects, and outreach statistics

## Tech Stack

### Backend
- Django 4.2.7
- Django REST Framework
- PostgreSQL
- Celery (for background tasks)
- Redis (for task queue)

### Frontend
- React 18
- Vite
- TailwindCSS
- React Query
- React Router

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

5. Update `.env` with your database credentials and settings.

6. Run migrations:
```bash
python manage.py migrate
```

7. Create a superuser:
```bash
python manage.py createsuperuser
```

8. Start the development server:
```bash
python manage.py runserver
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000` and the backend at `http://localhost:8000`.

### Celery Setup (Optional, for background scraping)

1. Start Redis:
```bash
redis-server
```

2. Start Celery worker:
```bash
cd backend
celery -A project_matcher worker -l info
```

3. Start Celery beat (for scheduled tasks):
```bash
celery -A project_matcher beat -l info
```

## Project Structure

```
timothy-llc/
├── backend/
│   ├── project_matcher/     # Django project settings
│   ├── users/                # User management app
│   ├── projects/             # Project leads and matching
│   ├── scrapers/             # Scraping and qualification
│   └── outreach/             # Outreach management
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── contexts/         # React contexts
│   │   └── services/         # API services
└── README.md
```

## Key Features

### 1. Project Aggregation
- Scrapes from compliant sources (RSS feeds, public APIs)
- Avoids ToS violations by focusing on publicly available data
- Supports multiple platforms with configurable scraping methods

### 2. Project Qualification
- AI-powered scoring for relevance and quality
- Rule-based qualification system (extensible to OpenAI)
- Automatic status management

### 3. Project Matching
- Matches projects with users based on:
  - Skills overlap
  - User priority level
  - Project quality scores
- Supports manual match selection

### 4. Outreach Management
- Email template system
- Track message status (draft, sent, delivered, opened, responded)
- Integration-ready for email services (SendGrid, AWS SES, etc.)

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login
- `GET /api/auth/profile/` - Get user profile

### Projects
- `GET /api/projects/leads/` - List project leads
- `GET /api/projects/leads/{id}/` - Get project details
- `POST /api/projects/leads/{id}/match/` - Find matches for project
- `GET /api/projects/leads/available/` - Get available projects

### Scrapers
- `GET /api/scrapers/jobs/` - List scraping jobs
- `POST /api/scrapers/scrape_platform/` - Trigger platform scraping
- `POST /api/scrapers/scrape_all/` - Trigger all platform scraping

### Outreach
- `GET /api/outreach/messages/` - List outreach messages
- `POST /api/outreach/messages/` - Create outreach message
- `POST /api/outreach/messages/{id}/send/` - Send message

## Development Notes

### Adding New Scraping Sources

1. Add a new `SourcePlatform` in Django admin or via API
2. Configure the scraping method (rss_feed, public_api, public_scrape)
3. Implement custom scraper if needed in `scrapers/scrapers.py`
4. Trigger scraping via API or Celery task

### Extending Qualification

The qualification system in `scrapers/qualifiers.py` can be extended:
- Add OpenAI integration for advanced qualification
- Add custom scoring rules
- Integrate with external APIs for company validation

### Email Integration

To enable actual email sending:
1. Configure email service (SendGrid, AWS SES, etc.)
2. Update `outreach/services.py` with email sending logic
3. Add email templates in Django admin

## License

Copyright © Timothy Morgan LLC. All rights reserved.

## Support

For questions or issues, please contact the development team.
