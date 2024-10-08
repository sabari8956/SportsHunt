# Generated by Django 5.0.1 on 2024-05-30 08:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisers', '0021_tournament_venue_link_alter_tournament_venue'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='registration',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='game',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournament_game', to='organisers.game'),
        ),
    ]
