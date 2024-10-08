# Generated by Django 5.0.1 on 2024-03-28 04:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisers', '0003_player_alter_team_members'),
    ]

    operations = [
        migrations.CreateModel(
            name='fixtures',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fixture', models.JSONField(blank=True)),
                ('winners_stages', models.JSONField(blank=True)),
                ('currentStage', models.IntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organisers.category')),
                ('currentBracket', models.ManyToManyField(blank=True, related_name='current_bracket', to='organisers.match')),
                ('currentWinners', models.ManyToManyField(blank=True, related_name='current_winners', to='organisers.team')),
            ],
        ),
    ]
