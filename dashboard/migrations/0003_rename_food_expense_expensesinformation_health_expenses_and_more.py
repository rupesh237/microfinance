# Generated by Django 4.2.14 on 2024-12-04 12:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_alter_center_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='expensesinformation',
            old_name='food_expense',
            new_name='health_expenses',
        ),
        migrations.RenameField(
            model_name='expensesinformation',
            old_name='health_expense',
            new_name='house_expenses',
        ),
        migrations.RenameField(
            model_name='incomeinformation',
            old_name='cattle_income',
            new_name='abroad_employment_income',
        ),
        migrations.RenameField(
            model_name='incomeinformation',
            old_name='earning',
            new_name='agriculture_income',
        ),
        migrations.RenameField(
            model_name='incomeinformation',
            old_name='farming_income',
            new_name='animal_farming_income',
        ),
        migrations.RemoveField(
            model_name='expensesinformation',
            name='house_rent',
        ),
    ]
