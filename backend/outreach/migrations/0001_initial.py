# Generated manually - Initial migration for outreach app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OutreachTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('subject', models.CharField(max_length=500)),
                ('body', models.TextField()),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'outreach_templates',
            },
        ),
        migrations.CreateModel(
            name='OutreachMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=500)),
                ('body', models.TextField()),
                ('recipient_email', models.EmailField(max_length=254)),
                ('recipient_name', models.CharField(blank=True, max_length=200, null=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('sent', 'Sent'), ('delivered', 'Delivered'), ('opened', 'Opened'), ('responded', 'Responded'), ('bounced', 'Bounced')], default='draft', max_length=20)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('opened_at', models.DateTimeField(blank=True, null=True)),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('response_text', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outreach_messages', to='projects.projectlead')),
                ('template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='outreach.outreachtemplate')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outreach_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'outreach_messages',
                'ordering': ['-created_at'],
            },
        ),
    ]
