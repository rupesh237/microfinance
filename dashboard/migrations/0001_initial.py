# Generated by Django 4.2.14 on 2024-11-14 12:25

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
                ('tole', models.CharField(blank=True, max_length=64, null=True)),
                ('wardNo', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Center',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='Active', max_length=25)),
                ('code', models.CharField(max_length=20, null=True)),
                ('input_code', models.CharField(max_length=20, null=True)),
                ('name', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('GENERAL', 'General'), ('PUBLIC', 'Public'), ('BUSINESS', 'Business'), ('OTHERS', 'Others')], default='general', max_length=15)),
                ('no_of_group', models.IntegerField(default=1, null=True)),
                ('no_of_members', models.IntegerField(default=4, null=True)),
                ('meeting_place', models.CharField(max_length=50, null=True)),
                ('meeting_distance', models.IntegerField(default=0, null=True)),
                ('formed_date', models.DateTimeField(auto_now_add=True)),
                ('meeting_start_date', models.DateTimeField(null=True)),
                ('meeting_start_time', models.TimeField(null=True)),
                ('meeting_end_time', models.TimeField(null=True)),
                ('walking_time', models.TimeField(null=True)),
                ('meeting_repeat_type', models.CharField(choices=[('fixed interval', 'Fixed Interval'), ('fixed date', 'Fixed Date')], max_length=25, null=True)),
                ('meeting_interval', models.IntegerField(choices=[(14, '14 days'), (28, '28 days')], default=14, null=True)),
                ('meeting_date', models.IntegerField(default=1, null=True)),
                ('every', models.IntegerField(default=1, null=True)),
                ('from_date', models.DateTimeField(null=True)),
                ('to_date', models.DateTimeField(null=True)),
                ('approved_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='app_by', to=settings.AUTH_USER_MODEL)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.branch')),
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
            name='GRoup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=100)),
                ('position', models.IntegerField(default=1)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='Active', max_length=50)),
                ('center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.center')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member_category', models.CharField(choices=[('Group Member', 'Group Member'), ('Public Member', 'Public Member')], default='General Member', max_length=20)),
                ('member_code', models.IntegerField(null=True)),
                ('code', models.CharField(max_length=20, null=True)),
                ('position', models.IntegerField(null=True)),
                ('status', models.CharField(choices=[('A', 'Active'), ('IA', 'In-Active'), ('RTR', 'Ready To Register'), ('D', 'Dropout'), ('p', 'Public'), ('D', 'Death')], default='RTR', max_length=25)),
                ('center', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.center')),
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
                ('first_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('phone_number', models.CharField(max_length=15, null=True)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Female', max_length=15)),
                ('marital_status', models.CharField(choices=[('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'), ('Widow', 'Widow')], max_length=30)),
                ('family_status', models.CharField(choices=[('Poor', 'Poor'), ('Medium', 'Medium'), ('High', 'High'), ('Rich', 'Rich')], max_length=20)),
                ('education', models.CharField(choices=[('Illiterate', 'Illiterate'), ('Literate', 'Literate'), ('Under SLC', 'High'), ('SLC', 'SLC'), ('Intermediate', 'Intermediate'), ('Bachelor', 'Bachelor'), ("Master's Degree", "Master's Degree"), ('Ph.D.', 'Ph.D.')], max_length=30)),
                ('religion', models.CharField(choices=[('Hinduism', 'Hinduism'), ('Buddhism', 'Buddhism'), ('Kirat', 'Kirat'), ('Christainity', 'Christainity'), ('Islam', 'Islam'), ('Jainism', 'Jainism'), ('Bon', 'Bon')], max_length=30)),
                ('occupation', models.CharField(choices=[('Agriculture', 'Agriculture'), ('Business', 'Business'), ('Housewife', 'Housewife'), ('Foreign Employment', 'Foreign Employment')], max_length=30)),
                ('family_member_no', models.IntegerField()),
                ('date_of_birth', models.DateField()),
                ('voter_id', models.CharField(blank=True, max_length=20, null=True)),
                ('voter_id_issued_on', models.DateField(blank=True, null=True)),
                ('citizenship_no', models.CharField(max_length=20)),
                ('issued_from', models.CharField(max_length=20)),
                ('issued_date', models.DateField()),
                ('marriage_reg_no', models.CharField(blank=True, max_length=20, null=True)),
                ('registered_vdc', models.CharField(blank=True, max_length=20, null=True)),
                ('marriage_regd_date', models.DateField(blank=True, null=True)),
                ('registered_date', models.DateField(auto_now_add=True)),
                ('file_no', models.IntegerField(blank=True, null=True)),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='personalInfo', to='dashboard.member')),
                ('registered_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Municipality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
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
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='livestockInfo', to='dashboard.member')),
            ],
        ),
        migrations.CreateModel(
            name='LandInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('farming_land', models.FloatField(default=0.0)),
                ('other_land', models.FloatField(default=0.0)),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='landInfo', to='dashboard.member')),
            ],
        ),
        migrations.CreateModel(
            name='IncomeInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('earning', models.FloatField(default=0.0)),
                ('farming_income', models.FloatField(default=0.0)),
                ('cattle_income', models.FloatField(default=0.0)),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='incomeInfo', to='dashboard.member')),
            ],
        ),
        migrations.CreateModel(
            name='HouseInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('concrete', models.BooleanField(default=False)),
                ('mud', models.BooleanField(default=False)),
                ('iron', models.BooleanField(default=False)),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='houseInfo', to='dashboard.member')),
            ],
        ),
        migrations.CreateModel(
            name='FamilyInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('family_member_name', models.CharField(max_length=50)),
                ('relationship', models.CharField(choices=[('Father', 'Father'), ('Husband', 'Husband'), ('Father-In-Law', 'Father-In-Law'), ('Son', 'Son'), ('Daughter', 'Daughter')], max_length=30)),
                ('date_of_birth', models.DateField()),
                ('citizenship_no', models.CharField(blank=True, max_length=20, null=True)),
                ('issued_from', models.CharField(blank=True, max_length=20, null=True)),
                ('issued_date', models.DateField(blank=True, null=True)),
                ('education', models.CharField(blank=True, choices=[('Illiterate', 'Illiterate'), ('Literate', 'Literate'), ('Under SLC', 'High'), ('SLC', 'SLC'), ('Intermediate', 'Intermediate'), ('Bachelor', 'Bachelor'), ("Master's Degree", "Master's Degree"), ('Ph.D.', 'Ph.D.')], max_length=30, null=True)),
                ('occupation', models.CharField(blank=True, max_length=30, null=True)),
                ('monthly_income', models.FloatField(blank=True, default=0.0, null=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='familyInfo', to='dashboard.member')),
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
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='expensesInfo', to='dashboard.member')),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone_number', models.CharField(max_length=20)),
                ('image', models.ImageField(blank=True, null=True, upload_to='users/')),
                ('citizenship_card', models.ImageField(blank=True, null=True, upload_to='users/')),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('manager', 'Manager'), ('employee', 'Employee')], max_length=10)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.branch')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='employee', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='district',
            name='province',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='districts', to='dashboard.province'),
        ),
        migrations.AddField(
            model_name='center',
            name='district',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='centerdistrict', to='dashboard.district'),
        ),
        migrations.AddField(
            model_name='center',
            name='formed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='formed_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='center',
            name='grt_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='grt_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='center',
            name='meeting_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='meeting_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='center',
            name='municipality',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='centermunicipality', to='dashboard.municipality'),
        ),
        migrations.AddField(
            model_name='center',
            name='pgt_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pgt_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='center',
            name='province',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='centerprovince', to='dashboard.province'),
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
        migrations.CreateModel(
            name='AddressInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permanent_ward_no', models.IntegerField(default=1)),
                ('permanent_tole', models.CharField(max_length=50)),
                ('permanent_house_no', models.CharField(blank=True, max_length=50, null=True)),
                ('current_ward_no', models.IntegerField(default=1)),
                ('current_tole', models.CharField(max_length=50)),
                ('current_house_no', models.CharField(blank=True, max_length=50, null=True)),
                ('old_ward_no', models.IntegerField(default=1)),
                ('old_tole', models.CharField(max_length=50)),
                ('old_house_no', models.CharField(blank=True, max_length=50, null=True)),
                ('current_district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_current_district', to='dashboard.district')),
                ('current_municipality', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_current_municipality', to='dashboard.municipality')),
                ('current_province', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_current_province', to='dashboard.province')),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='addressInfo', to='dashboard.member')),
                ('old_district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_old_district', to='dashboard.district')),
                ('old_municipality', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_old_municipality', to='dashboard.municipality')),
                ('old_province', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_old_province', to='dashboard.province')),
                ('permanent_district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_permanent_district', to='dashboard.district')),
                ('permanent_municipality', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_permanent_municipality', to='dashboard.municipality')),
                ('permanent_province', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_permanent_province', to='dashboard.province')),
            ],
        ),
    ]
