# Generated by Django 3.0.2 on 2020-01-13 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0002_auto_20200112_1259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grades',
            name='masterteacher',
        ),
    ]
