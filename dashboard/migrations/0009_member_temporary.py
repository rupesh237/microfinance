# Generated by Django 4.2.14 on 2025-02-18 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_alter_personalmemberdocument_uploaded_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='temporary',
            field=models.BooleanField(default=True),
        ),
    ]
