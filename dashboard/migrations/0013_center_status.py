# Generated by Django 5.1 on 2024-10-04 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_alter_center_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='center',
            name='status',
            field=models.CharField(default='Active', max_length=25),
        ),
    ]
