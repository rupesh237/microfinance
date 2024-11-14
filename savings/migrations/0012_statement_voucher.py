# Generated by Django 5.1 on 2024-11-11 10:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_voucher_category'),
        ('savings', '0011_statement_by_alter_statement_transaction_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='statement',
            name='voucher',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='statement_voucher', to='core.voucher'),
            preserve_default=False,
        ),
    ]
