# Generated by Django 3.2.9 on 2021-12-18 06:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_alter_event_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='enroll',
            options={'verbose_name': 'Запись', 'verbose_name_plural': 'Записи'},
        ),
    ]
