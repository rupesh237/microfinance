# Generated by Django 4.2.13 on 2024-07-07 06:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=3)),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Center',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=100)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.branch')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=100)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.center')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.group')),
            ],
        ),
        migrations.CreateModel(
            name='Province',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PersonalInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=20)),
                ('current_address', models.TextField()),
                ('permanent_address', models.TextField()),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dashboard.member')),
            ],
        ),
        migrations.CreateModel(
            name='Municipality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('tole', models.CharField(max_length=64)),
                ('wardNo', models.IntegerField()),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='municipalities', to='dashboard.district')),
            ],
        ),
        migrations.CreateModel(
            name='LivestockInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cows', models.IntegerField(default=0)),
                ('buffalo', models.IntegerField(default=0)),
                ('goat', models.IntegerField(default=0)),
                ('sheep', models.IntegerField(default=0)),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dashboard.member')),
            ],
        ),
        migrations.CreateModel(
            name='LandInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('farming_land', models.FloatField(default=0.0)),
                ('other_land', models.FloatField(default=0.0)),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dashboard.member')),
            ],
        ),
        migrations.CreateModel(
            name='IncomeInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('earning', models.FloatField(default=0.0)),
                ('farming_income', models.FloatField(default=0.0)),
                ('cattle_income', models.FloatField(default=0.0)),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dashboard.member')),
            ],
        ),
        migrations.CreateModel(
            name='HouseInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('concrete', models.BooleanField(default=False)),
                ('mud', models.BooleanField(default=False)),
                ('iron', models.BooleanField(default=False)),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dashboard.member')),
            ],
        ),
        migrations.CreateModel(
            name='FamilyInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sons', models.IntegerField(default=0)),
                ('daughters', models.IntegerField(default=0)),
                ('husband', models.CharField(blank=True, max_length=100, null=True)),
                ('father', models.CharField(blank=True, max_length=100, null=True)),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dashboard.member')),
            ],
        ),
        migrations.CreateModel(
            name='ExpensesInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('house_rent', models.FloatField(default=0.0)),
                ('food_expense', models.FloatField(default=0.0)),
                ('health_expense', models.FloatField(default=0.0)),
                ('other_expenses', models.FloatField(default=0.0)),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dashboard.member')),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone_number', models.CharField(max_length=20)),
                ('image', models.ImageField(blank=True, null=True, upload_to='employee_images/')),
                ('citizenship_card', models.ImageField(blank=True, null=True, upload_to='citizenship_cards/')),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('manager', 'Manager'), ('employee', 'Employee')], max_length=10)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.branch')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='district',
            name='province',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='districts', to='dashboard.province'),
        ),
        migrations.AddField(
            model_name='branch',
            name='district',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='branches', to='dashboard.district'),
        ),
        migrations.AddField(
            model_name='branch',
            name='municipality',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='branches', to='dashboard.municipality'),
        ),
        migrations.AddField(
            model_name='branch',
            name='province',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='branches', to='dashboard.province'),
        ),
    ]