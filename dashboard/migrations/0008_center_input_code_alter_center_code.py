# Generated by Django 5.1 on 2024-10-03 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_alter_center_formed_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='center',
            name='input_code',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='center',
            name='code',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
