# Generated by Django 5.0.1 on 2024-03-15 10:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_rename_is_organizer_user_is_organiser'),
        ('organisers', '0002_tournament_venue'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='cart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='organisers.team'),
        ),
    ]
