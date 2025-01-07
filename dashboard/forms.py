from django import forms
from django.forms.widgets import DateInput, TimeInput
from django.utils import timezone

from . models import Branch, Employee, District, Municipality, Center, Member
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import AddressInformation, PersonalInformation, FamilyInformation, LivestockInformation, LandInformation, HouseInformation, IncomeInformation, ExpensesInformation, GRoup
from .models import Province, District, Municipality
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
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

        return cleaned_data
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EmployeeForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    

class CenterForm(forms.ModelForm):
    formed_date_display = forms.DateTimeField(label="Formed Date", required=False, 
                                              widget=forms.DateTimeInput(attrs={'readonly': 'readonly'}))
    class Meta:
        model = Center
        fields = ['input_code', 'name', 'branch', 'province', 'district', 'municipality', 'category', 'no_of_group', 'no_of_members', 'meeting_place', 'meeting_distance', 'formed_by', 'meeting_start_date', 'meeting_start_time', 'meeting_end_time', 'walking_time', 'meeting_by', 'meeting_repeat_type', 'meeting_interval', 'meeting_date', 'every', 'pgt_by', 'from_date', 'to_date', 'grt_by', 'approved_by' ]
        widgets = {
            'meeting_start_time': TimeInput(attrs={'type': 'time'}),
            'meeting_end_time': TimeInput(attrs={'type': 'time'}),
            'walking_time': TimeInput(attrs={'type': 'time'}),
            'meeting_repeat_type': forms.Select(attrs={'id': 'id_meeting_repeat_type'}),
            'meeting_interval': forms.Select(attrs={'id': 'id_meeting_interval'}),
            'meeting_date': forms.NumberInput(attrs={'id': 'id_meeting_date'}),
            'every': forms.NumberInput(attrs={'id': 'id_every'}),

        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CenterForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        # Disable only the 'every' field
        self.fields['every'].disabled = True
        self.fields['formed_date_display'].disabled = True
        self.fields['district'].queryset = District.objects.none()
        self.fields['municipality'].queryset = Municipality.objects.none()

        # If editing an existing center, use the saved formed_date value (formatted to date only)
        if self.instance and self.instance.pk:
            self.fields['formed_date_display'].initial = self.instance.formed_date.date()

             # Set initial values for district and municipality if they exist
            if self.instance.district:
                self.fields['district'].initial = self.instance.district.id
            if self.instance.municipality:
                self.fields['municipality'].initial = self.instance.municipality.id
        else:
            # If adding a new center, use the current date (without time)
            self.fields['formed_date_display'].initial = timezone.now().date()

        # Handle province change for district
        if 'province' in self.data:
            try:
                province_id = int(self.data.get('province'))
                self.fields['district'].queryset = District.objects.filter(province_id=province_id).order_by('name')

            except (ValueError, TypeError):
                pass
        elif self.instance and self.instance.province:
            # If editing, set district queryset based on the province of the instance
            self.fields['district'].queryset = District.objects.filter(province_id=self.instance.branch.province.id).order_by('name')

        # Handle district change for municipality
        if 'district' in self.data:
            try:
                district_id = int(self.data.get('district'))
                self.fields['municipality'].queryset = Municipality.objects.filter(district_id=district_id).order_by('name')

            except (ValueError, TypeError):
                pass
        elif self.instance and self.instance.district:
            # If editing, set municipality queryset based on the district of the instance
            self.fields['municipality'].queryset = Municipality.objects.filter(district_id=self.instance.district.id).order_by('name')

        # Hide the branch field when updating
        if self.instance and self.instance.pk:
            self.fields['branch'].widget = forms.HiddenInput()
        
        # Check if user is passed and is authenticated
        if user and user.is_authenticated:
            # If the user is superuser, show all branches
            if user.is_superuser:
                self.fields['branch'].queryset = Branch.objects.all()
            else:
                try:
                    # Check if the user is an employee
                    employee = user.employee
                    # If the user's role is 'admin', show all branches
                    if employee.role == 'admin':
                        self.fields['branch'].queryset = Branch.objects.all()
                    else:
                        # Otherwise, limit to the user's specific branch
                        self.fields['branch'].queryset = Branch.objects.filter(id=employee.branch.id)
                
                # Handle case where employee profile doesn't exist
                except Employee.DoesNotExist:
                    self.fields['branch'].queryset = Branch.objects.none()
        else:
            # If no user is provided, set an empty queryset or handle it appropriately
            self.fields['branch'].queryset = Branch.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')

        # Validate that both dates are provided
        if from_date and to_date:
            # Check that the difference is exactly 7 days
            if (to_date - from_date).days != 7:
                raise ValidationError('The "to date" must be exactly 7 days after the "from date".')
        return cleaned_data

    def save(self, commit=True):
        center = super(CenterForm, self).save(commit=False)

        # Get the branch code
        branch_code = self.cleaned_data['branch'].code
        print(branch_code)

        # Format the code field as <branch_code>.<user_inputted_code>
        user_input_code = self.cleaned_data['input_code']
        print(user_input_code)
        center.code = f"{branch_code}.{user_input_code}"
        print(center)

        if commit:
            center.save()
        return center
                
class GroupForm(forms.ModelForm):
    position = forms.ChoiceField(choices=[])
    
    class Meta:
        model = GRoup  # Adjust the model name here
        fields = ['center', 'position', 'code', 'name']

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        # Disable all fields except 'name' when editing an existing group
        if self.instance and self.instance.pk:
            self.fields['center'].disabled = True
            self.fields['position'].disabled = True
            self.fields['code'].disabled = True

            # Retain the previous choices for the 'position' field
            self.fields['position'].choices = [(i, i) for i in range(1, self.instance.center.no_of_group + 1)]
        else:
            # Dynamically populate 'position' based on the selected center
            if 'center' in self.data:
                try:
                    center_id = int(self.data.get('center'))
                    center = Center.objects.get(id=center_id)
                    self.fields['position'].choices = [(i, i) for i in range(1, center.no_of_group + 1)]
                    # Ensure the selected value is retained
                    if 'position' in self.data:
                        self.fields['position'].initial = self.data.get('position')
                except (ValueError, TypeError, Center.DoesNotExist):
                    self.fields['position'].choices = []
            else:
                self.fields['position'].choices = []
            
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


    def clean(self):
        cleaned_data = super().clean()
        center = cleaned_data.get('center')

        if center and self.instance.pk:
            # Exclude the current group from the count when updating
            existing_groups_count = GRoup.objects.filter(center=center).exclude(pk=self.instance.pk).count()

            if existing_groups_count >= center.no_of_group:
                raise ValidationError(f'The number of groups for this center has reached the maximum limit of {center.no_of_group}.')
        elif center:
            # This check is for new group creation
            existing_groups_count = GRoup.objects.filter(center=center).count()

            if existing_groups_count >= center.no_of_group:
                raise ValidationError(f'The number of groups for this center has reached the maximum limit of {center.no_of_group}.')
        
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

class PersonalInformationForm(forms.ModelForm):
    class Meta:
        model = PersonalInformation
        fields = ['first_name', 'middle_name', 'last_name', 'phone_number', 'gender', 'marital_status', 'family_status', 'education', 'religion',
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
        

    def __init__(self, *args, **kwargs):
        relationships = kwargs.pop('relationships', [])
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        if 'relationship' in self.initial and self.initial['relationship'] in relationships:
            self.fields['relationship'].widget.attrs.update({
                'readonly': 'readonly',
                'disabled': 'disabled',
            })

    def clean_relationship(self):
        relationship = self.cleaned_data.get('relationship')
        if self.fields['relationship'].widget.attrs.get('disabled'):
            return self.initial.get('relationship')  # Return the preset relationship
        return relationship





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