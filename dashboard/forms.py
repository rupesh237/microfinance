from django import forms
from . models import Branch, Employee, District, Municipality, Center, Member
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import PersonalInformation, FamilyInformation, LivestockInformation, LandInformation, HouseInformation, IncomeInformation, ExpensesInformation, GRoup

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['code', 'name', 'province', 'district', 'municipality']

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
    class Meta:
        model = Center
        fields = ['branch', 'code', 'name', 'no_of_group', 'no_of_members']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CenterForm, self).__init__(*args, **kwargs)

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
        fields = ['center', 'group', 'member_code', 'code']

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



class PersonalInformationForm(forms.ModelForm):
    class Meta:
        model = PersonalInformation
        fields = ['name', 'phone_number', 'current_address', 'permanent_address']

class FamilyInformationForm(forms.ModelForm):
    class Meta:
        model = FamilyInformation
        fields = ['sons', 'daughters', 'husband', 'father']

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
        fields = ['farming_land', 'other_land']

class IncomeInformationForm(forms.ModelForm):
    class Meta:
        model = IncomeInformation
        fields = ['earning', 'farming_income', 'cattle_income']

class ExpensesInformationForm(forms.ModelForm):
    class Meta:
        model = ExpensesInformation
        fields = ['house_rent', 'food_expense', 'health_expense', 'other_expenses']