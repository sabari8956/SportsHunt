# Generated by Django 5.0.1 on 2024-06-03 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisers', '0022_category_registration_alter_tournament_game'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='payment_method',
            field=models.BooleanField(default=True),
        ),
    ]
