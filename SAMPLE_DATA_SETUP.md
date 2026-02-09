# Sample Data Setup Guide

This guide will help you populate the database with example projects to showcase the frontend.

## Quick Start

### 1. Run Migrations (if not done already)
```bash
cd timothy-llc/backend
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Sample Data
```bash
python manage.py create_sample_data
```

This will create:
- 3 sample source platforms
- 12 sample projects (all marked as public)
- System settings (free_projects_limit = 12)

### 3. View the Results

**Public Projects Page:**
- Navigate to: `http://localhost:3000/public`
- You should see 12 sample projects

**Django Admin:**
- Navigate to: `http://localhost:8000/admin`
- Login with your superuser credentials
- Check "Project Leads" to see all sample projects
- Check "System Settings" to adjust the free projects limit

## Sample Projects Included

The command creates 12 diverse projects including:

1. **Full-Stack Web Application Development** - React & Django
2. **E-commerce Platform** - React & Node.js
3. **Mobile App Development** - iOS & Android
4. **Python Backend API** - Django REST Framework
5. **Frontend Developer** - React Dashboard
6. **WordPress Migration** - Custom Platform
7. **Blockchain Integration** - Smart Contracts
8. **DevOps Engineer** - CI/CD Pipeline
9. **UI/UX Designer + Developer** - Design & Development
10. **Machine Learning Model** - Recommendation System
11. **API Integration Specialist** - Third-party APIs
12. **Database Optimization** - PostgreSQL

Each project includes:
- Realistic title and description
- Company name
- Budget range (USD)
- Required skills
- Project type
- Quality and relevance scores
- Public visibility enabled

## Clearing and Recreating

To clear existing sample data and create fresh data:

```bash
python manage.py create_sample_data --clear
```

This will:
- Delete existing sample projects
- Delete sample platforms
- Create fresh sample data

## Adjusting Free Projects Limit

### Via Django Admin:
1. Go to `http://localhost:8000/admin/projects/systemsettings/`
2. Edit the `free_projects_limit` setting
3. Change the value (e.g., from 12 to 20)
4. Save

### Via Django Shell:
```python
python manage.py shell
>>> from projects.models import SystemSettings
>>> setting = SystemSettings.objects.get(key='free_projects_limit')
>>> setting.value = '20'
>>> setting.save()
```

### Via API (if authenticated):
```bash
# Get current settings
GET /api/projects/settings/

# Update free_projects_limit
PUT /api/projects/settings/{id}/
{
  "key": "free_projects_limit",
  "value": "20",
  "description": "Number of free projects shown to non-authenticated users"
}
```

## Testing the Application Flow

1. **View Public Projects:**
   - Visit `http://localhost:3000/public`
   - Browse the 12 sample projects
   - Click on any project to see details

2. **View Project Details:**
   - Click "View Details" on any project
   - See full project information
   - Skills, budget, description, etc.

3. **Submit Application:**
   - Click "Apply Now" button
   - Fill out the application form
   - Submit (no login required)

4. **View Applications (Admin):**
   - Login to Django admin
   - Go to "Project Applications"
   - See all submitted applications
   - Update status, add notes

## Customizing Sample Data

To customize the sample projects, edit:
`timothy-llc/backend/projects/management/commands/create_sample_data.py`

You can:
- Add more projects to the `projects_data` list
- Modify project details
- Change budget ranges
- Update skills lists
- Adjust scores

Then run the command again with `--clear` flag.

## Troubleshooting

### No projects showing?
- Check that projects are marked as `is_public=True`
- Verify system settings exist: `free_projects_limit`
- Check project status is 'new' or 'qualified'

### Wrong number of projects?
- Check the `free_projects_limit` setting value
- Ensure enough projects are marked as public
- Verify projects have status 'new' or 'qualified'

### Projects not visible in admin?
- Make sure you're logged in as superuser
- Check that migrations ran successfully
- Verify the `projects` app is in `INSTALLED_APPS`

## Next Steps

After setting up sample data:
1. Test the public projects page
2. Submit a test application
3. View applications in admin
4. Adjust free projects limit
5. Customize project data as needed
