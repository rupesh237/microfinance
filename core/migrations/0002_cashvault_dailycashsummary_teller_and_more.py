# Generated by Django 4.2.14 on 2025-01-22 08:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0002_alter_employee_branch_alter_employee_user_and_more'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CashVault',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('last_updated', models.DateTimeField()),
                ('pending_amount', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True)),
                ('branch', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cash_vault', to='dashboard.branch')),
            ],
        ),
        migrations.CreateModel(
            name='DailyCashSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opening_vault_balance', models.DecimalField(decimal_places=2, max_digits=12)),
                ('closing_vault_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('teller_balances', models.JSONField(default=dict)),
                ('date', models.DateField()),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_summaries', to='dashboard.branch')),
            ],
        ),
        migrations.CreateModel(
            name='Teller',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('pending_amount', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tellers', to='dashboard.branch')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TellerToTellerTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('description', models.TextField(blank=True, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved')], default='Pending', max_length=30)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.branch')),
                ('from_teller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='core.teller')),
                ('to_teller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='core.teller')),
            ],
        ),
        migrations.CreateModel(
            name='VaultTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('Deposit', 'Deposit'), ('Withdraw', 'Withdraw')], max_length=30)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('description', models.TextField(blank=True, null=True)),
                ('deposited_by', models.CharField(blank=True, max_length=100, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved')], default='Pending', max_length=30)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.branch')),
                ('cash_vault', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='core.cashvault')),
                ('teller', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='core.teller')),
            ],
        ),
        migrations.DeleteModel(
            name='CashManagement',
        ),
    ]
