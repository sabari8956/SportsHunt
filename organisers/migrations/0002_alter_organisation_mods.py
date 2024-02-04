# Generated by Django 5.0.1 on 2024-02-04 18:13

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='mods',
            field=models.ManyToManyField(blank=True, related_name='organisation_mod', to=settings.AUTH_USER_MODEL),
        ),
    ]