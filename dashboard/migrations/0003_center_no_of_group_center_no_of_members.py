# Generated by Django 5.1 on 2024-08-16 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_alter_employee_citizenship_card_alter_employee_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='center',
            name='no_of_group',
            field=models.IntegerField(default=1, null=True),
        ),
        migrations.AddField(
            model_name='center',
            name='no_of_members',
            field=models.IntegerField(default=4, null=True),
        ),
    ]
