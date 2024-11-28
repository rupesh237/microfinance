# Generated by Django 4.2.14 on 2024-11-21 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_alter_center_formed_date_alter_center_from_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='center',
            name='formed_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='center',
            name='from_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='center',
            name='meeting_start_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='center',
            name='meeting_start_time',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='center',
            name='to_date',
            field=models.DateTimeField(null=True),
        ),
    ]