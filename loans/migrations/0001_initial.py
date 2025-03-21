# Generated by Django 4.2.14 on 2025-01-09 06:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EMIPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_date', models.DateField(auto_now_add=True)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('principal_paid', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('interest_paid', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_type', models.CharField(choices=[('Flat', 'Flat Interest'), ('Declining', 'Declining Balance'), ('Interest_Only', 'Interest Only')], max_length=20)),
                ('loan_purpose', models.CharField(choices=[('Crop and Crop Services', 'Crop and Crop Services'), ('Wholesale and Retail Business', 'Wholesale and Retail Business'), ('Hotel and Restaurants', 'Hotel and Restaurants'), ('Fruits and Flowers', 'Fruits and Flowers'), ('Animal Husbandary', 'Animal Husbandary'), ('Poultry', 'Poultry'), ('Other Agricultural and Agro Services', 'Other Agricultural and Agro Services'), ('Other Services', 'Other Services')], max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('loan_demand_date', models.DateField()),
                ('loan_disburse_date', models.DateField()),
                ('status', models.CharField(choices=[('applied', 'Applied'), ('analysis', 'Analysis'), ('disburse', 'Disburse'), ('approved', 'Approved'), ('active', 'Active'), ('closed', 'Closed')], default='applied', max_length=100)),
                ('is_cleared', models.BooleanField(default=False)),
                ('loan_analysis_date', models.DateField(blank=True, null=True)),
                ('loan_analysis_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('approved_date', models.DateField(blank=True, null=True)),
                ('interest_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('duration_months', models.IntegerField(blank=True, default=0, null=True)),
                ('installement_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('created_date', models.DateField(blank=True, null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_loans', to=settings.AUTH_USER_MODEL)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loans', to='dashboard.member')),
                ('payments', models.ManyToManyField(blank=True, related_name='loans', to='loans.emipayment')),
            ],
        ),
        migrations.AddField(
            model_name='emipayment',
            name='loan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emi_payments', to='loans.loan'),
        ),
    ]
