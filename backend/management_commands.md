# Management Commands

## Create Superuser
```bash
python manage.py createsuperuser
```

## Run Migrations
```bash
python manage.py migrate
```

## Create Migrations
```bash
python manage.py makemigrations
```

## Load Initial Data (Optional)
You can create a management command or use Django admin to add initial source platforms.

## Start Development Server
```bash
python manage.py runserver
```

## Start Celery Worker
```bash
celery -A project_matcher worker -l info
```

## Start Celery Beat (Scheduler)
```bash
celery -A project_matcher beat -l info
```
