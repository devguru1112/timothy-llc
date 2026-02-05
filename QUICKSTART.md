# Quick Start Guide

## Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL (or use SQLite for development)
- Redis (optional, for Celery background tasks)

## Quick Setup (5 minutes)

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example and update)
cp .env.example .env

# For quick testing, you can use SQLite instead of PostgreSQL
# Edit .env and comment out DATABASE settings, or update settings.py temporarily

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### 2. Frontend Setup

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### 3. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

## First Steps

1. **Login** with your superuser credentials
2. **Add Source Platforms** via Admin panel:
   - Go to http://localhost:8000/admin
   - Navigate to "Source Platforms"
   - Add platforms (e.g., RSS feeds, job boards)
3. **Configure Your Profile**:
   - Go to Settings
   - Add your skills
   - Set your priority level
4. **Start Scraping**:
   - Use the API endpoint `/api/scrapers/scrape_platform/` or
   - Use Django admin to trigger scraping jobs

## Testing the System

### Manual Project Creation (for testing)

1. Go to Django Admin
2. Navigate to "Project Leads"
3. Add a test project manually
4. View it in the frontend at `/projects`

### Testing Matching

1. Create a project with skills: `["React", "Django", "Python"]`
2. Update your user profile with matching skills
3. Use the "Find Matches" button on the project detail page
4. Check the matches in the API or admin

## Next Steps

- Configure email service for outreach (see README.md)
- Set up Celery for automated scraping
- Add more source platforms
- Customize qualification rules

## Troubleshooting

### Database Issues
- Make sure PostgreSQL is running (or switch to SQLite)
- Check `.env` file has correct database credentials

### CORS Issues
- Ensure `CORS_ALLOWED_ORIGINS` in `settings.py includes `http://localhost:3000`

### Frontend Not Connecting
- Check that backend is running on port 8000
- Verify Vite proxy configuration in `vite.config.js`
