# Generated by Django 5.1 on 2024-10-30 11:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0006_alter_savingsaccount_account_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='savingsaccount',
            old_name='interest',
            new_name='interest_rate',
        ),
    ]