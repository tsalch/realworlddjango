# Generated by Django 3.2.9 on 2021-12-16 12:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_alter_event_is_private'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='events.category'),
        ),
    ]
