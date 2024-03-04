# Generated by Django 5.0.1 on 2024-03-04 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisers', '0007_remove_tournament_catogories_alter_tournament_game'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='price',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tournament',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='tournament_catagory', to='organisers.category'),
        ),
    ]
