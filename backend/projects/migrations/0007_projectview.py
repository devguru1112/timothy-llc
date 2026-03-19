from django.conf import settings
from django.db import migrations, models
from django.db.models import deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0006_run_setup_initial_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=deletion.CASCADE, related_name='views', to='projects.projectlead')),
                ('user', models.ForeignKey(on_delete=deletion.CASCADE, related_name='project_views', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'project_views',
                'unique_together': {('project', 'user')},
            },
        ),
        migrations.AddIndex(
            model_name='projectview',
            index=models.Index(fields=['user', 'viewed_at'], name='project_views_user_viewed_at_idx'),
        ),
    ]
