# Generated by Django 3.2.9 on 2021-12-17 19:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_auto_20211217_2220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='events.event', verbose_name='Событие'),
        ),
    ]
