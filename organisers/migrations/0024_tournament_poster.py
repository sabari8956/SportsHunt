# Generated by Django 5.0.1 on 2024-06-11 19:19

import organisers.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisers', '0023_team_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='poster',
            field=models.ImageField(blank=True, null=True, upload_to=organisers.models.Tournament.upload_to, verbose_name='poster'),
        ),
    ]
