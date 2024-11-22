# Generated by Django 4.2.14 on 2024-11-21 11:46

from django.db import migrations, models
import nepali_datetime_field.models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='center',
            name='formed_date',
            field=nepali_datetime_field.models.NepaliDateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='center',
            name='from_date',
            field=nepali_datetime_field.models.NepaliDateField(null=True),
        ),
        migrations.AlterField(
            model_name='center',
            name='meeting_start_date',
            field=nepali_datetime_field.models.NepaliDateField(null=True),
        ),
        migrations.AlterField(
            model_name='center',
            name='meeting_start_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='center',
            name='to_date',
            field=nepali_datetime_field.models.NepaliDateField(null=True),
        ),
    ]
