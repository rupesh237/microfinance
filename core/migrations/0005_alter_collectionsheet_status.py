# Generated by Django 4.2.14 on 2024-12-07 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_collectionsheet_supervision_by_2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionsheet',
            name='status',
            field=models.CharField(choices=[('Saved', 'Saved'), ('Submitted', 'Submitted'), ('Approved', 'Approved'), ('Accepted', 'Accepted'), ('Cancelled', 'Cancelled')], default='Saved', max_length=100),
        ),
    ]
