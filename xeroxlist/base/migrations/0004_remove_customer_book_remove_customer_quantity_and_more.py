# Generated by Django 5.0 on 2024-01-10 09:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_alter_order_user_customerorder'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='book',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='total_price',
        ),
        migrations.RemoveField(
            model_name='order',
            name='book',
        ),
        migrations.AlterField(
            model_name='customer',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
