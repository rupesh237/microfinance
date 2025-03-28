# Generated by Django 4.2.14 on 2025-03-06 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_member_temporary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='status',
            field=models.CharField(choices=[('A', 'Active'), ('IA', 'In-Active'), ('RTR', 'Ready To Register'), ('DR', 'Dropout'), ('p', 'Public'), ('D', 'Death')], default='RTR', max_length=25),
        ),
    ]
