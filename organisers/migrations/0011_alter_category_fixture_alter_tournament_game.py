# Generated by Django 5.0.1 on 2024-03-28 06:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisers', '0010_alter_fixtures_fixture_alter_fixtures_winners_stages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='fixture',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='this_fixture', to='organisers.fixtures'),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='game',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournament_game', to='organisers.game'),
        ),
    ]