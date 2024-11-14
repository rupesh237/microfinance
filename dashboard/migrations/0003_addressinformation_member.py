# Generated by Django 5.1 on 2024-10-29 09:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_alter_familyinformation_member_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='addressinformation',
            name='member',
            field=models.OneToOneField(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='adressInfo', to='dashboard.member'),
            preserve_default=False,
        ),
    ]