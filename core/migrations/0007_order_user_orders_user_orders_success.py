# Generated by Django 5.0.1 on 2024-05-25 05:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_user_otp_user_otptime_user_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('amount', models.IntegerField()),
                ('status', models.CharField(max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='orders',
            field=models.ManyToManyField(blank=True, related_name='orders_all', to='core.order'),
        ),
        migrations.AddField(
            model_name='user',
            name='orders_success',
            field=models.ManyToManyField(blank=True, related_name='orders_paid', to='core.order'),
        ),
    ]
