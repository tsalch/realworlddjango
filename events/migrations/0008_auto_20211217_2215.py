# Generated by Django 3.2.9 on 2021-12-17 19:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_alter_event_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enroll',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Создана'),
        ),
        migrations.AlterField(
            model_name='enroll',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='enrolls', to='events.event', verbose_name='Событие'),
        ),
    ]