# Generated by Django 5.0.1 on 2024-01-31 14:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_user_email'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': [('organiser', 'can create tournaments [ hosts] ')]},
        ),
    ]