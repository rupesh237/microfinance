# Generated by Django 4.2.14 on 2024-08-01 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='citizenship_card',
            field=models.ImageField(blank=True, null=True, upload_to='users/'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='users/'),
        ),
    ]