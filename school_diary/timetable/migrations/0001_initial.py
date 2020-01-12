# Generated by Django 3.0.2 on 2020-01-12 07:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Grades',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('letter', models.CharField(max_length=1)),
                ('masterteacher', models.CharField(max_length=80)),
            ],
            options={
                'verbose_name': 'Класс',
                'verbose_name_plural': 'Классы',
                'ordering': ['number', 'letter'],
            },
        ),
        migrations.CreateModel(
            name='Lessons',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(max_length=15)),
                ('number', models.IntegerField()),
                ('start', models.TimeField()),
                ('end', models.TimeField()),
                ('subject', models.CharField(max_length=50)),
                ('classroom', models.IntegerField()),
                ('connection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.Grades')),
            ],
            options={
                'verbose_name': 'Урок',
                'verbose_name_plural': 'Уроки',
                'ordering': ['day', 'number'],
            },
        ),
    ]
