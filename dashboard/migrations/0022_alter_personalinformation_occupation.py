# Generated by Django 5.1 on 2024-10-26 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0021_alter_familyinformation_member'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personalinformation',
            name='occupation',
            field=models.CharField(choices=[('Agriculture', 'Agriculture'), ('Business', 'Business'), ('Housewife', 'Housewife'), ('Foreign Employment', 'Foreign Employment')], max_length=30),
        ),
    ]