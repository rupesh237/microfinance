# Generated by Django 4.2.14 on 2024-08-01 12:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_alter_employee_citizenship_card_alter_employee_image'),
        ('savings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecurringDeposit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('duration', models.PositiveIntegerField(help_text='Duration in months')),
                ('interest_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recurring_deposits', to='dashboard.member')),
            ],
        ),
        migrations.CreateModel(
            name='FixedDeposit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('interest_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('maturity_date', models.DateField()),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fixed_deposits', to='dashboard.member')),
            ],
        ),
    ]