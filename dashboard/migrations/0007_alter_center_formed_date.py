# Generated by Django 5.1 on 2024-10-03 08:12

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_remove_center_created_by_remove_center_created_on_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='center',
            name='formed_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]