# Generated by Django 5.1 on 2024-11-18 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0002_loan_is_cleared'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='status',
            field=models.CharField(choices=[('applied', 'Applied'), ('analysis', 'Analysis'), ('active', 'Active'), ('closed', 'Closed')], default='applied', max_length=100),
        ),
    ]
