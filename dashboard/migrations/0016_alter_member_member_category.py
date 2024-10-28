# Generated by Django 5.1 on 2024-10-04 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0015_member_status_alter_member_member_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='member_category',
            field=models.CharField(choices=[('Group Member', 'Group Member'), ('Public Member', 'Public Member')], default='General Member', max_length=20),
        ),
    ]