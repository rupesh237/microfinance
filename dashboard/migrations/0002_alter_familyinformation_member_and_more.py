# Generated by Django 5.1 on 2024-10-29 08:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='familyinformation',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='familyInfo', to='dashboard.member'),
        ),
        migrations.AlterField(
            model_name='personalinformation',
            name='occupation',
            field=models.CharField(choices=[('Agriculture', 'Agriculture'), ('Business', 'Business'), ('Housewife', 'Housewife'), ('Foreign Employment', 'Foreign Employment')], max_length=30),
        ),
    ]
