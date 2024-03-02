# Generated by Django 5.0.1 on 2024-02-13 13:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisers', '0002_alter_organisation_mods'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254, unique=True, verbose_name='tournament name')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('game', models.CharField(choices=[('Badminton', 'badminton'), ('Tennis', 'tennis')], default='Badminton', max_length=254, verbose_name='game type')),
                ('mods', models.ManyToManyField(blank=True, related_name='tournament_mod', to=settings.AUTH_USER_MODEL)),
                ('org', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organisers.organisation')),
            ],
        ),
    ]