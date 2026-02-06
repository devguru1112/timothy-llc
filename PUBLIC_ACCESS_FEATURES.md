# Public Access Features

## Overview

The system now supports public project browsing and application submission without requiring user authentication. This allows visitors to explore projects and apply before signing up.

## Features Implemented

### 1. Admin-Controlled Free Project Limit
- **SystemSettings Model**: Admins can control how many free projects are shown to non-authenticated users
- **Setting Key**: `free_projects_limit` (default: 10)
- **Admin Interface**: Manage via Django admin at `/admin/projects/systemsettings/`

### 2. Public Project Browsing
- **Endpoint**: `/api/projects/leads/public/`
- **Access**: No authentication required
- **Features**:
  - View limited number of public projects (controlled by admin)
  - See project details: title, description, company, budget, skills
  - Filtered to show only public projects with status 'new' or 'qualified'

### 3. Project Application System
- **Model**: `ProjectApplication` - stores applications from non-authenticated users
- **Endpoint**: `/api/projects/applications/` (POST for create, no auth required)
- **Features**:
  - Submit applications without signing up
  - Includes: name, email, phone, portfolio, skills, cover letter
  - Prevents duplicate applications (by email per project)
  - Links to user account if they sign up later

### 4. Public Frontend Pages
- **Public Projects Page**: `/public` - Browse available projects
- **Public Project Detail**: `/public/projects/:id` - View project details and apply
- **Application Form**: Modal form for submitting applications

## Setup Instructions

### 1. Run Migrations
```bash
cd timothy-llc/backend
python manage.py makemigrations
python manage.py migrate
```

### 2. Set Up Initial Settings
```bash
python manage.py shell
>>> from scripts.setup_initial_settings import setup_settings
>>> setup_settings()
```

Or manually create in Django admin:
- Go to `/admin/projects/systemsettings/`
- Add new setting:
  - Key: `free_projects_limit`
  - Value: `10` (or your desired number)
  - Description: `Number of free projects shown to non-authenticated users`

### 3. Mark Projects as Public
- Go to Django admin: `/admin/projects/projectlead/`
- Edit projects and check the "Is public" checkbox
- Only public projects will be visible to non-authenticated users

## API Endpoints

### Public Endpoints (No Authentication)

#### Get Public Projects
```
GET /api/projects/leads/public/
Response: {
  "count": 10,
  "limit": 10,
  "results": [...]
}
```

#### Get Public Project Detail
```
GET /api/projects/leads/{id}/
(Returns limited fields for non-authenticated users)
```

#### Submit Application
```
POST /api/projects/applications/
Body: {
  "project": 1,
  "applicant_name": "John Doe",
  "applicant_email": "john@example.com",
  "applicant_phone": "+1234567890",
  "applicant_portfolio": "https://portfolio.com",
  "applicant_skills": ["React", "Django"],
  "cover_letter": "I'm interested in..."
}
```

### Admin Endpoints (Authentication Required)

#### Manage System Settings
```
GET /api/projects/settings/ - List all settings
POST /api/projects/settings/ - Create new setting
PUT /api/projects/settings/{id}/ - Update setting
```

## Frontend Routes

- `/public` - Public projects listing page
- `/public/projects/:id` - Public project detail page with application form
- `/login` - Sign in page
- `/register` - Sign up page (to be implemented)

## Admin Features

### System Settings Management
1. Navigate to Django admin
2. Go to "System Settings"
3. Create or edit the `free_projects_limit` setting
4. Set the value to control how many free projects are shown

### Project Visibility Control
1. Go to "Project Leads" in admin
2. Edit any project
3. Check/uncheck "Is public" to control visibility
4. Only public projects appear in the public listing

### Application Management
1. Go to "Project Applications" in admin
2. View all applications submitted
3. Update status: pending → reviewed → contacted/rejected
4. Add internal notes

## Security Considerations

1. **Rate Limiting**: Consider adding rate limiting to prevent abuse
2. **Email Validation**: Applications validate email format
3. **Duplicate Prevention**: Same email cannot apply twice to same project
4. **Project Validation**: Only public projects in valid status can receive applications
5. **Data Privacy**: Contact information is only shown to authenticated users

## Future Enhancements

- [ ] Email notifications when applications are received
- [ ] Application status tracking for applicants
- [ ] CAPTCHA for application form
- [ ] Application analytics dashboard
- [ ] Bulk application export
- [ ] Application templates/auto-responses
