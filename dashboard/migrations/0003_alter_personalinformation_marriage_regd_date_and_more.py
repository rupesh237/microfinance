# Generated by Django 4.2.14 on 2024-12-17 10:32

from django.db import migrations
import nepali_datetime_field.models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_alter_addressinformation_member'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personalinformation',
            name='marriage_regd_date',
            field=nepali_datetime_field.models.NepaliDateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='personalinformation',
            name='registered_date',
            field=nepali_datetime_field.models.NepaliDateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='personalinformation',
            name='voter_id_issued_on',
            field=nepali_datetime_field.models.NepaliDateField(blank=True, null=True),
        ),
    ]
