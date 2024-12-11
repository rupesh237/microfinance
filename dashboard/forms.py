from django import forms
from django.forms.widgets import DateInput, TimeInput
from django.utils import timezone

from . models import Branch, Employee, District, Municipality, Center, Member
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import AddressInformation, PersonalInformation, FamilyInformation, LivestockInformation, LandInformation, HouseInformation, IncomeInformation, ExpensesInformation, GRoup

class BranchForm(forms.ModelForm):
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
    

class CenterForm(forms.ModelForm):
    formed_date_display = forms.DateTimeField(label="Formed Date", required=False, 
                                              widget=forms.DateTimeInput(attrs={'readonly': 'readonly'}))
    class Meta:
        model = Center
        fields = ['input_code', 'name', 'branch', 'province', 'district', 'municipality', 'category', 'no_of_group', 'no_of_members', 'meeting_place', 'meeting_distance', 'formed_by', 'meeting_start_date', 'meeting_start_time', 'meeting_end_time', 'walking_time', 'meeting_by', 'meeting_repeat_type', 'meeting_interval', 'meeting_date', 'every', 'pgt_by', 'from_date', 'to_date', 'grt_by', 'approved_by' ]
        widgets = {
            'meeting_start_date': DateInput(attrs={'type': 'date'}),
            'meeting_start_time': TimeInput(attrs={'type': 'time'}),
            'meeting_end_time': TimeInput(attrs={'type': 'time'}),
            'walking_time': TimeInput(attrs={'type': 'time'}),
            'from_date': DateInput(attrs={'type': 'date'}),
            'to_date': DateInput(attrs={'type': 'date'}),
            'meeting_repeat_type': forms.Select(attrs={'id': 'id_meeting_repeat_type'}),
            'meeting_interval': forms.Select(attrs={'id': 'id_meeting_interval'}),
            'meeting_date': forms.NumberInput(attrs={'id': 'id_meeting_date'}),
            'every': forms.NumberInput(attrs={'id': 'id_every'}),

        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CenterForm, self).__init__(*args, **kwargs)
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

        # If editing an existing instance, populate the group field with groups from the selected center
        if 'center' in self.data:
            try:
                center_id = int(self.data.get('center'))
                self.fields['group'].queryset = GRoup.objects.filter(center_id=center_id)
                
                center = Center.objects.get(id=center_id)
                max_member_code = center.no_of_group * center.no_of_members
                self.fields['member_code'].choices = [(i, i) for i in range(1, max_member_code + 1)]
            except (ValueError, TypeError, Center.DoesNotExist):
                self.fields['group'].queryset = GRoup.objects.none()
                self.fields['member_code'].choices = []
        elif self.instance.pk:
            center = self.instance.center
            self.fields['group'].queryset = GRoup.objects.filter(center=center)
            max_member_code = center.no_of_group * center.no_of_members
            self.fields['member_code'].choices = [(i, i) for i in range(1, max_member_code + 1)]
        else:
            self.fields['group'].queryset = GRoup.objects.none()
            self.fields['member_code'].choices = []

    def clean_member_code(self):
        member_code = self.cleaned_data.get('member_code')
        center = self.cleaned_data.get('center')
        
        if center and member_code:
            # Check if the member_code is already used in the given center
            if Member.objects.filter(center=center, member_code=member_code).exists():
                raise ValidationError(f"The member code {member_code} is already used in this center.")
        
        return member_code


class AddressInformationForm(forms.ModelForm):
    class Meta:
        model = AddressInformation
        fields = ['permanent_province', 'permanent_district', 'permanent_municipality', 'permanent_ward_no', 'permanent_tole', 'permanent_house_no',
                'current_province', 'current_district', 'current_municipality', 'current_ward_no', 'current_tole', 'current_house_no',
                'old_province', 'old_district', 'old_municipality', 'old_ward_no', 'old_tole', 'old_house_no',]

class PersonalInformationForm(forms.ModelForm):
    class Meta:
        model = PersonalInformation
        fields = ['first_name', 'middle_name', 'last_name', 'phone_number', 'gender', 'marital_status', 'family_status', 'education', 'religion',
                   'occupation', 'family_member_no', 'date_of_birth', 'voter_id', 'voter_id_issued_on', 'citizenship_no', 'issued_from', 'issued_date', 'marriage_reg_no',
                   'registered_vdc', 'marriage_regd_date', 'registered_by', 'file_no',
         ]
        widgets = {
            'date_of_birth': DateInput(attrs={'type': 'date'}),
            'issued_date': DateInput(attrs={'type': 'date'}),
            'marriage_regd_date': DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # print("Cleaned data:", cleaned_data)
        return cleaned_data


class FamilyInformationForm(forms.ModelForm):
    class Meta:
        model = FamilyInformation
        fields = [
            'family_member_name', 'relationship', 'date_of_birth', 
            'citizenship_no', 'issued_from', 'issued_date', 
            'education', 'occupation', 'monthly_income', 'phone_number'
        ]
        widgets = {
            'date_of_birth': DateInput(attrs={'type': 'date'}),
            'issued_date': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # Capture predefined relationships if passed
        self.relationships = kwargs.pop('relationships', None)
        super().__init__(*args, **kwargs)

        # Set up choices for relationship field if relationships are provided
        if self.relationships:
            self.fields['relationship'] = forms.ChoiceField(choices=[(rel, rel) for rel in self.relationships])

            # Disable relationship field for predefined relationships (first three)
            if self.initial.get('relationship') in self.relationships[:3]:
                self.fields['relationship'].widget.attrs['readonly'] = True
                self.fields['relationship'].widget.attrs['disabled'] = True
            else:
                # Ensure it's enabled for dynamically added family members
                self.fields['relationship'].widget.attrs.pop('disabled', None)
                self.fields['relationship'].widget.attrs.pop('readonly', None)

    def clean_relationship(self):
        relationship = self.cleaned_data.get('relationship')
        
        # Return initial if field is disabled for predefined relationships
        if self.fields['relationship'].widget.attrs.get('disabled'):
            return self.initial.get('relationship')  # Preset relationship remains

        if not relationship:
            raise forms.ValidationError("This field is required.")
        return relationship

    def clean(self):
        cleaned_data = super().clean()
        relationship = cleaned_data.get('relationship')
        
        # Require specific fields if relationship is 'Husband'
        if relationship == 'Husband':
            required_fields = ['citizenship_no', 'issued_from', 'issued_date']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f"{field.replace('_', ' ').capitalize()} is required for Husband.")
                    
        return cleaned_data




class LivestockInformationForm(forms.ModelForm):
    class Meta:
        model = LivestockInformation
        fields = ['cows', 'buffalo', 'goat', 'sheep']

class HouseInformationForm(forms.ModelForm):
    class Meta:
        model = HouseInformation
        fields = ['concrete', 'mud', 'iron']

class LandInformationForm(forms.ModelForm):
    class Meta:
        model = LandInformation
        fields = [ 'farming_land','other_land']
        widgets = {
            'farming_land': forms.TextInput(attrs={'placeholder': 'Farming Land (Dhur)'}),
            'other_land': forms.TextInput(attrs={'placeholder': 'Other Land (Dhur)'})
        }

class IncomeInformationForm(forms.ModelForm):
    class Meta:
        model = IncomeInformation
        fields = ['agriculture_income', 'animal_farming_income', 'business_income', 'abroad_employment_income', 'wages_income', 'personal_job_income', 'government_post', 'pension', 'other']

class ExpensesInformationForm(forms.ModelForm):
    class Meta:
        model = ExpensesInformation
        fields = ['house_expenses', 'education_expenses', 'health_expenses', 'festival_expenses', 'clothes_expenses', 'communication_expenses', 'fuel_expenses', 'entertaiment_expenses', 'other_expenses']