# Generated by Django 5.0.1 on 2024-03-10 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='venue',
            field=models.CharField(default='TBA', max_length=254, verbose_name='Venue'),
        ),
    ]
