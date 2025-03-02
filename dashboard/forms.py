from django import forms
from django.forms.widgets import DateInput, TimeInput
from django.utils import timezone

from . models import Branch, Employee, District, Municipality, Center, Member
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import AddressInformation, PersonalInformation, PersonalMemberDocument, FamilyMemberDocument, FamilyInformation, LivestockInformation, LandInformation, HouseInformation, IncomeInformation, ExpensesInformation, GRoup
from .models import Province, District, Municipality

from  nepali_datetime_field.forms import NepaliDateInput

class BranchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BranchForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    class Meta:
        model = Branch
        fields = '__all__'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['district'].queryset = District.objects.none()
            self.fields['municipality'].queryset = Municipality.objects.none()
        
            if 'province' in self.data:
                try:
                    province_id = int(self.data.get('province'))
                    self.fields['district'].queryset = District.objects.filter(province_id=province_id).order_by('name')

                except (ValueError, TypeError):
                    pass

            if 'district' in self.data:
                try:
                    district_id = int(self.data.get('district'))
                    self.fields['municipality'].queryset = Municipality.objects.filter(district_id=district_id).order_by('name')

                except (ValueError, TypeError):
                    pass
            
    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get('code')
        branch_name = cleaned_data.get('name')

        if code:
            existing_branch = Branch.objects.filter(code=code).exclude(id=self.instance.id if self.instance else None)
            if existing_branch.exists():
                self.add_error('code', 'Branch with this code already exists.')
        
        if branch_name:
            existing_branch = Branch.objects.filter(name=branch_name).exclude(id=self.instance.id if self.instance else None)
            if existing_branch.exists():
                self.add_error('name', 'Branch with this name already exists.')
        
        return cleaned_data
    


class EmployeeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Employee
        fields = ['name', 'email', 'phone_number', 'image', 'citizenship_card', 'role', 'branch', 'password', 'confirm_password']
        widgets = {
            'role': forms.Select(choices=[('admin', 'Admin'), ('manager', 'Manager'), ('employee', 'Employee')])
        }

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        branch = cleaned_data.get('branch')
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if role == "manager":
            existing_manager = Employee.objects.filter(branch=branch,role=role).exclude(id=self.instance.id if self.instance else None)
            if existing_manager.exists():
                self.add_error('role', "Only one manager can be assigned to a branch.")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

        return cleaned_data
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.fields['branch'].queryset = self.get_branch_queryset(user)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def get_branch_queryset(self, user):
        """Returns queryset for the center field based on user role."""
        if not user or not user.is_authenticated:
            return Branch.objects.none()

        if user.is_superuser:
            return Branch.objects.all()

        try:
            employee = user.employee_detail
            if employee.role == 'admin':
                return Branch.objects.all()
            return Branch.objects.filter(id=employee.branch.id)
        except AttributeError:
            return Branch.objects.none()
    
    

class CenterForm(forms.ModelForm):
    formed_date_display = forms.DateTimeField(
        label="Formed Date", required=False, 
        widget=forms.DateTimeInput(attrs={'readonly': 'readonly'}))
    class Meta:
        model = Center
        fields = ['input_code', 'name', 'branch', 'province', 'district', 'municipality', 'category', 'no_of_group', 'no_of_members', 'meeting_place', 'meeting_distance', 'formed_by', 'meeting_start_date', 'meeting_start_time', 'meeting_end_time', 'walking_time', 'meeting_by', 'meeting_repeat_type', 'meeting_interval', 'meeting_date', 'every', 'pgt_by', 'from_date', 'to_date', 'grt_by', 'approved_by' ]
        widgets = {
            'meeting_start_date': DateInput(attrs={'type': 'date'}),
            'meeting_start_time': TimeInput(attrs={'type': 'time'}),
            'meeting_end_time': TimeInput(attrs={'type': 'time'}),
            'from_date': DateInput(attrs={'type': 'date'}),
            'to_date': DateInput(attrs={'type': 'date'}),
            # 'walking_time': TimeInput(attrs={'type': 'time'}),
            'meeting_repeat_type': forms.Select(attrs={'id': 'id_meeting_repeat_type'}),
            'meeting_interval': forms.Select(attrs={'id': 'id_meeting_interval'}),
            'meeting_date': forms.NumberInput(attrs={'id': 'id_meeting_date'}),
            'every': forms.NumberInput(attrs={'id': 'id_every'}),

        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CenterForm, self).__init__(*args, **kwargs)

        self.fields['branch'].queryset = self.get_branch_queryset(user)
        self.apply_field_classes()
        self.configure_initial_values()
        self.set_dynamic_querysets()
        
    def apply_field_classes(self):
        """Apply Bootstrap form-control class to all fields."""
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def configure_initial_values(self):
        """Set initial values for read-only and dependent fields."""
        if self.instance and self.instance.pk:
            self.fields['formed_date_display'].initial = self.instance.formed_date.date()
            self.fields['branch'].widget = forms.HiddenInput()
        else:
            self.fields['formed_date_display'].initial = timezone.now().date()

        self.fields['every'].disabled = True
        self.fields['formed_date_display'].disabled = True

    def set_dynamic_querysets(self):
        """Set queryset for district and municipality dynamically."""
        self.fields['district'].queryset = District.objects.filter(
            province_id=int(self.data.get('province', self.instance.province.id if self.instance and self.instance.province else 0))
        ) if 'province' in self.data or (self.instance and self.instance.province) else District.objects.none()

        self.fields['municipality'].queryset = Municipality.objects.filter(
            district_id=int(self.data.get('district', self.instance.district.id if self.instance and self.instance.district else 0))
        ) if 'district' in self.data or (self.instance and self.instance.district) else Municipality.objects.none()
    
    
    def get_branch_queryset(self, user):
        """Returns queryset for the center field based on user role."""
        if not user or not user.is_authenticated:
            return Branch.objects.none()
        if user.is_superuser:
            return Branch.objects.all()
        try:
            employee = user.employee_detail
            if employee.role == 'admin':
                return Branch.objects.all()
            return Branch.objects.filter(id=employee.branch.id)
        except AttributeError:
            return Branch.objects.none()
        
    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')
        input_code = cleaned_data.get('input_code')
        branch = cleaned_data['branch']

        # Validate that both dates are provided
        if from_date and to_date:
            # Check that the difference is exactly 7 days
            if (to_date - from_date).days != 7:
                raise ValidationError('The "to date" must be exactly 7 days after the "from date".')
            
            # Ensure input_code is unique within the same branch
        if input_code and branch:
            existing_center = Center.objects.filter(input_code=input_code, branch=branch).exclude(id=self.instance.id if self.instance else None)
            if existing_center.exists():
                self.add_error('input_code', 'This input code already exists for this branch. Please choose a different one.')
                
        return cleaned_data

    def save(self, commit=True):
        center = super(CenterForm, self).save(commit=False)

        # Get the branch code
        branch_code = self.cleaned_data['branch'].code
        # print(branch_code)

        # Format the code field as <branch_code>.<user_inputted_code>
        user_input_code = self.cleaned_data['input_code']
        # print(user_input_code)
        center.code = f"{branch_code}.{user_input_code}"
        # print(center)

        if commit:
            center.save()
        return center
                
class GroupForm(forms.ModelForm):
    position = forms.ChoiceField(choices=[])
    
    class Meta:
        model = GRoup 
        fields = ['center', 'position', 'code', 'name']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(GroupForm, self).__init__(*args, **kwargs)

        center_queryset = self.get_center_queryset(user)
        self.fields['center'].queryset = center_queryset

        # Disable fields except 'name' when editing an existing group
        if self.instance.pk:
            # Ensure the current instance's center is included in the queryset
            if self.instance.center and self.instance.center not in center_queryset:
                self.fields['center'].queryset = Center.objects.filter(id=self.instance.center.id) | center_queryset
            self.fields['center'].disabled = True
            self.fields['position'].disabled = True
            self.fields['code'].disabled = True

            self.fields['position'].choices = self.get_position_choices(self.instance.center)
        else:
            self.fields['position'].choices = self.get_dynamic_position_choices()

        # Apply Bootstrap class
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def get_position_choices(self, center):
        """Returns position choices based on the center's no_of_group."""
        return [(i, i) for i in range(1, center.no_of_group + 1)] if center else []
    
    def get_dynamic_position_choices(self):
        """Handles dynamically populating the position field based on selected center."""
        center_id = self.data.get('center')
        if center_id:
            try:
                center = Center.objects.get(id=int(center_id))
                return self.get_position_choices(center)
            except (ValueError, TypeError, Center.DoesNotExist):
                return []
        return []

    def get_center_queryset(self, user):
        """Returns queryset for the center field based on user role."""
        if not user or not user.is_authenticated:
            return Center.objects.none()

        if user.is_superuser:
            return Center.objects.all()

        try:
            employee = user.employee_detail
            if employee.role == 'admin':
                return Center.objects.all()
            return Center.objects.filter(branch=employee.branch)
        except AttributeError:
            return Center.objects.none()
        
    def clean(self):
        cleaned_data = super().clean()
        center = cleaned_data.get('center')
        name = cleaned_data.get('name')

        if not center:
            return cleaned_data

        # Count existing groups excluding current one (if updating)
        existing_groups_count = GRoup.objects.filter(center=center).exclude(pk=self.instance.pk).count()

        if existing_groups_count >= center.no_of_group:
            self.add_error('center', f'Maximum {center.no_of_group} groups allowed for this center.')

        if name and center:
            existing_group = GRoup.objects.filter(name=name, center=center).exclude(id=self.instance.id if self.instance else None)
            if existing_group.exists():
                self.add_error('name', 'Group with this name already exists. Please choose a different one.')

        return cleaned_data


class GroupSelectionForm(forms.Form):
    group = forms.ModelChoiceField(queryset=GRoup.objects.all(), label="Select Group...")

class CenterSelectionForm(forms.ModelForm):
    center = forms.ModelChoiceField(queryset=Center.objects.all(), label="Center")
    group = forms.ModelChoiceField(queryset=GRoup.objects.none(), label="Group")
    member_code = forms.ChoiceField()

    class Meta:
        model = Member  # Ensure this references the correct model
        fields = ['member_category', 'center', 'group', 'member_code', 'code', 'position']

    def __init__(self, *args, **kwargs):
        super(CenterSelectionForm, self).__init__(*args, **kwargs)

        # Add 'form-control' class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        center = None
        if 'center' in self.data:
            try:
                center_id = int(self.data.get('center'))
                center = Center.objects.get(id=center_id)
            except (ValueError, TypeError, Center.DoesNotExist):
                pass
        elif self.instance.pk:
            center = self.instance.center

        if center:
            self.populate_fields(center)

    def populate_fields(self, center):
        """Helper method to populate group and member_code fields based on the center."""
        self.fields['group'].queryset = GRoup.objects.filter(center=center)
        max_member_code = center.no_of_group * center.no_of_members if center.no_of_group and center.no_of_members else 0
        self.fields['member_code'].choices = [(i, i) for i in range(1, max_member_code + 1)]

    def clean_member_code(self):
        member_code = self.cleaned_data.get('member_code')
        center = self.cleaned_data.get('center')

        if center and member_code:
            if Member.objects.filter(center=center, member_code=member_code).exists():
                raise ValidationError(f"The member code {member_code} is already used in this center.")

        return member_code


class AddressInformationForm(forms.ModelForm):
    # Fields for current address
    current_province = forms.ModelChoiceField(queryset=Province.objects.all(), label="Current Province")
    current_district = forms.ModelChoiceField(queryset=District.objects.none(), label="Current District")
    current_municipality = forms.ModelChoiceField(queryset=Municipality.objects.none(), label="Current Municipality")
    current_ward_no = forms.IntegerField(label="Current Ward No")
    current_tole = forms.CharField(label="Current Tole")
    current_house_no = forms.CharField(label="Current House No", required=False)

    # Fields for permanent address
    same_as_current_permanent = forms.BooleanField(
        label="Same as Current Address (Permanent)", required=False
    )
    permanent_province = forms.ModelChoiceField(queryset=Province.objects.all(), label="Permanent Province")
    permanent_district = forms.ModelChoiceField(queryset=District.objects.none(), label="Permanent District")
    permanent_municipality = forms.ModelChoiceField(queryset=Municipality.objects.none(), label="Permanent Municipality")
    permanent_ward_no = forms.IntegerField(label="Permanent Ward No")
    permanent_tole = forms.CharField(label="Permanent Tole")
    permanent_house_no = forms.CharField(label="Permanent House No", required=False)

    # Fields for old address
    same_as_current_old = forms.BooleanField(
        label="Same as Current Address (Old)", required=False
    )
    old_province = forms.ModelChoiceField(queryset=Province.objects.all(), label="Old Province", required=False)
    old_district = forms.ModelChoiceField(queryset=District.objects.none(), label="Old District", required=False)
    old_municipality = forms.ModelChoiceField(queryset=Municipality.objects.none(), label="Old Municipality", required=False)
    old_ward_no = forms.IntegerField(label="Old Ward No", required=False)
    old_tole = forms.CharField(label="Old Tole", required=False)
    old_house_no = forms.CharField(label="Old House No", required=False)

    class Meta:
        model = AddressInformation
        fields = []  # All fields are handled manually.

    def __init__(self, *args, **kwargs):
        super(AddressInformationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'same_as_current_permanent' or field_name != 'same_as_current_old':
                field.widget.attrs['class'] = 'form-control'

        # Dynamically set queryset for district and municipality fields
        for address_type in ['current', 'permanent', 'old']:
            province_field = f"{address_type}_province"
            district_field = f"{address_type}_district"
            municipality_field = f"{address_type}_municipality"

            if province_field in self.data:
                try:
                    province_id = int(self.data.get(province_field))
                    self.fields[district_field].queryset = District.objects.filter(province_id=province_id)
                except (ValueError, TypeError):
                    self.fields[district_field].queryset = District.objects.none()

            if district_field in self.data:
                try:
                    district_id = int(self.data.get(district_field))
                    self.fields[municipality_field].queryset = Municipality.objects.filter(district_id=district_id)
                except (ValueError, TypeError):
                    self.fields[municipality_field].queryset = Municipality.objects.none()

            # Pre-fill fields based on initial data or instance
            if self.initial.get(province_field):
                self.fields[district_field].queryset = District.objects.filter(province=self.initial[province_field])

            if self.initial.get(district_field):
                self.fields[municipality_field].queryset = Municipality.objects.filter(district=self.initial[district_field])

    def clean(self):
        cleaned_data = super().clean()

        # Handle "Same as Current Address" for permanent and old addresses
        if cleaned_data.get('same_as_current_permanent'):
            for field in ['province', 'district', 'municipality', 'ward_no', 'tole', 'house_no']:
                cleaned_data[f"permanent_{field}"] = cleaned_data.get(f"current_{field}")

        if cleaned_data.get('same_as_current_old'):
            for field in ['province', 'district', 'municipality', 'ward_no', 'tole', 'house_no']:
                cleaned_data[f"old_{field}"] = cleaned_data.get(f"current_{field}")

        return cleaned_data


class PersonalMemberDocumentForm(forms.ModelForm):
    class Meta:
        model = PersonalMemberDocument
        fields = ['document_type', 'document_file',]

class PersonalInformationForm(forms.ModelForm):
    class Meta:
        model = PersonalInformation
        fields = ['first_name', 'middle_name', 'last_name', 'photo', 'phone_number', 'gender', 'marital_status', 'family_status', 'education', 'religion',
                   'occupation', 'family_member_no', 'date_of_birth', 'voter_id', 'voter_id_issued_on', 'citizenship_no', 'issued_from', 'issued_date', 'marriage_reg_no',
                   'registered_vdc', 'marriage_regd_date', 'registered_by', 'file_no',
         ]
        
        def __init__(self, *args, **kwargs):
            super(PersonalInformationForm, self).__init__(*args, **kwargs)
            for field_name, field in self.fields.items():
                field.widget.attrs['class'] = 'form-control'


class FamilyInformationForm(forms.ModelForm):
    class Meta:
        model = FamilyInformation
        fields = [
            'family_member_name', 'relationship', 'date_of_birth', 
            'citizenship_no', 'issued_from', 'issued_date', 
            'education', 'occupation', 'monthly_income', 'phone_number'
        ]

        widgets = {
            'date_of_birth': NepaliDateInput(attrs={'class': 'form-control nepali-date-field'}),
            'issued_date': NepaliDateInput(attrs={'class': 'form-control nepali-date-field'}),
        }
        
    def __init__(self, *args, **kwargs):
        super(FamilyInformationForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name not in ['date_of_birth', 'issued_date']:
                field.widget.attrs['class'] = 'form-control'


class LivestockInformationForm(forms.ModelForm):
    class Meta:
        model = LivestockInformation
        fields = ['cows', 'buffalo', 'goat', 'sheep']

    def __init__(self, *args, **kwargs):
        super(LivestockInformationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class HouseInformationForm(forms.ModelForm):
    class Meta:
        model = HouseInformation
        fields = ['concrete', 'mud', 'iron']

    def __init__(self, *args, **kwargs):
        super(HouseInformationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class LandInformationForm(forms.ModelForm):
    class Meta:
        model = LandInformation
        fields = [ 'farming_land','other_land']
        widgets = {
            'farming_land': forms.TextInput(attrs={'placeholder': 'Farming Land (Dhur)'}),
            'other_land': forms.TextInput(attrs={'placeholder': 'Other Land (Dhur)'})
        }

    def __init__(self, *args, **kwargs):
        super(LandInformationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class IncomeInformationForm(forms.ModelForm):
    class Meta:
        model = IncomeInformation
        fields = ['agriculture_income', 'animal_farming_income', 'business_income', 'abroad_employment_income', 'wages_income', 'personal_job_income', 'government_post', 'pension', 'other']

    def __init__(self, *args, **kwargs):
        super(IncomeInformationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class ExpensesInformationForm(forms.ModelForm):
    class Meta:
        model = ExpensesInformation
        fields = ['house_expenses', 'education_expenses', 'health_expenses', 'festival_expenses', 'clothes_expenses', 'communication_expenses', 'fuel_expenses', 'entertaiment_expenses', 'other_expenses']

    def __init__(self, *args, **kwargs):
        super(ExpensesInformationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'