from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
import nepali_datetime
from django.db import transaction

from django.views.generic import (
    CreateView, ListView, UpdateView, DeleteView )

from dashboard.models import Employee, Province, District, Municipality, Branch, GRoup, Member, Center,AddressInformation, PersonalInformation, FamilyInformation, LivestockInformation, HouseInformation, LandInformation, IncomeInformation, ExpensesInformation
from savings.models import SavingsAccount, INITIAL_SAVING_ACCOUNT_TYPE, Statement

from dashboard.forms import BranchForm, EmployeeForm, CenterForm, GroupForm

from .mixins import RoleRequiredMixin

from django.utils import timezone
from datetime import date, datetime


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    elif request.method == "POST":
        username= request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username= username, password= password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Invalid Username or Password!")
        return render(request, "dashboard/login.html")

    return render(request, "dashboard/login.html")


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    try:
        employee = Employee.objects.get(user= request.user)
        if employee.role == 'admin':
            return redirect('admin_dashboard')
        elif employee.role == 'manager':
            return redirect('manager_dashboard')
        else:
            return redirect('employee_dashboard')
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found!! please contact to the Admin')        
        return redirect('login')
    
@login_required
def admin_dashboard(request):
    members =Member.objects.all().select_related('personalInfo')
    for member in members:
        address_info = member.address_info.filter(address_type='current').first()

    groups = GRoup.objects.all()
    centers = Center.objects.all()
    employees = Employee.objects.all()
    return render(request, "dashboard/admin_dashboard.html",{
        'bank': 'Admin',
        'groups': groups,
        'centers': centers,
        'employees': employees,
        'members': members,
        'address_info': address_info,
    })

@login_required
def manager_dashboard(request):
    employee = Employee.objects.get(user= request.user)
    branch = employee.branch
    return render(request, "dashboard/manager_dashboard.html",{
        'branch': branch,
        'bank': 'Manager'
    })

@login_required
def employee_dashboard(request):
    employee = Employee.objects.get(user= request.user)
    branch = employee.branch
    return render(request, "dashboard/employee_dashboard.html",{
        'branch': branch,
        'bank': 'Staff'
    })

@login_required
def add_branch(request):
    if request.method =="POST":
        form = BranchForm(request.POST)
        if form.is_valid:
            form.save()
            return redirect('branch_list')
        else:
            messages.error(request, 'Error saving branch, please try again')
    form = BranchForm()
    return render(request, "branch/add_branch.html",{
        'form': form
    })

@login_required
def update_branch(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    form = BranchForm(instance=branch)
    # can also check the user status or the user role
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            branch = form.save()
            message=messages.success(request, 'Successfully updated the branch!!')
            return redirect('branch_list')

        return messages.error(request, form.errors)
    return render(request, 'branch/update_branch.html',{
        'form': form,
        'branch': branch
    })

@login_required
def delete_branch(request, pk):
    branch = get_object_or_404(Branch, pk)
    if request.method == 'POST':
        branch.delete()
        return redirect('branch_list')
    return messages.error(request, 'Error while deleting branch, please try again')

@login_required
def add_employee(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            # Create the user instance
            user = User.objects.create_user(
                username=cleaned_data['email'],
                email=cleaned_data['email'],
                password=cleaned_data['password']
            )
            # Create the employee instance but do not save to the database yet
            employee = form.save(commit=False)
            # Assign the user to the employee
            employee.user = user
            # Save the employee instance
            employee.save()
            return redirect('employee_list')
        else:
            messages.error(request, 'Error while adding Employee, please try again')
    else:
        form = EmployeeForm()
    
    return render(request, 'employee/add_employee.html', {
        'form': form
    })


def load_districts(request):
    province_id = request.GET.get('province')
    if province_id:
        districts = District.objects.filter(province_id=province_id).order_by('name')
        return JsonResponse(list(districts.values('id', 'name')), safe=False)
    return JsonResponse({'error': 'No province provided'}, status=400)

def load_municipalities(request):
    district_id = request.GET.get('district')
    municipalities = Municipality.objects.filter(district_id=district_id).order_by('name')
    return JsonResponse(list(municipalities.values('id', 'name')), safe=False)

def load_branches(request):
    district_id = request.GET.get('district')
    branches = Branch.objects.filter(district_id=district_id).order_by('name')
    return JsonResponse(list(branches.values('id', 'name')), safe=False)


## CENTER ##
class CenterListView(LoginRequiredMixin, ListView):
    model = Center
    context_object_name = 'centers'
    template_name = 'center/center_list.html'


class CenterCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Center
    form_class = CenterForm
    template_name = 'center/add_center.html'
    success_url = reverse_lazy('center_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Set the user who created the center
        form.instance.created_by = self.request.user
        # Save the center instance to access its ID
        center = form.save()

        # Check if groups should be created automatically
        if self.request.POST.get('create_groups') == 'yes':
            no_of_groups = form.cleaned_data.get('no_of_group', 0)  # Assuming there's a field for the number of groups
            for i in range(no_of_groups):
                GRoup.objects.create(center=center,
                                      name=f"{center.name}0{i + 1}", 
                                      code=f"{center.code}.{i+1}", 
                                      position=i+1, 
                                      created_by=self.request.user
                                    )  # Create groups with names

        messages.success(self.request, 'Center added successfully!')
        return super().form_valid(form)
    

    def form_invalid(self, form):
        messages.error(self.request, 'Error adding center, please check the form data')
        return super().form_invalid(form)
    
class CenterUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Center
    form_class = CenterForm
    template_name = 'center/edit_center.html'
    success_url = reverse_lazy('center_list')

    def get_form_kwargs(self):
        kwargs =  super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class CenterDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Center
    success_url = reverse_lazy('center_list')
    template_name = 'center/delete_center.html'


## GROUPS ##
class GroupListView(LoginRequiredMixin, ListView):
    model = GRoup
    context_object_name = 'groups'
    template_name = 'group/group_list.html'

def get_center_code(request, center_id):
    try:
        center = Center.objects.get(id=center_id)
        return JsonResponse({'code': center.code})
    except Center.DoesNotExist:
        return JsonResponse({'error': 'Center not found'}, status=404)
    
def get_no_of_groups(request, center_id):
    try:
        center = Center.objects.get(id=center_id)
        return JsonResponse({'no_of_group': center.no_of_group})
    except Center.DoesNotExist:
        return JsonResponse({'error': 'Center not found'}, status=404)


class GroupCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = GRoup
    form_class = GroupForm
    template_name = 'group/add_group.html'
    success_url = reverse_lazy('group_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
    
class GroupUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = GRoup
    form_class = GroupForm
    template_name = 'group/edit_group.html'
    success_url = reverse_lazy('group_list')

class GroupDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = GRoup
    success_url = reverse_lazy('group_list')
    template_name = 'group/delete_group.html'

from .forms import CenterSelectionForm
class SelectCenterView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Member
    form_class = CenterSelectionForm
    template_name = 'dashboard/select_center.html'
    template_name = 'member/add_member/select_center.html'
    success_url = reverse_lazy('address_info') 

    def form_valid(self, form):
        # Store center and group information in the session instead of saving the Member
        center_id = form.cleaned_data['center'].id
        group_id = form.cleaned_data['group'].id
        member_code = form.cleaned_data['member_code']
        member_category = form.cleaned_data['member_category']
        code = form.cleaned_data['code']
        position = form.cleaned_data['position']
        print(f"{center_id} {group_id} {member_code} {member_category} {code} {position}")
        
        # Store these details in the session
        self.request.session['center_id'] = center_id
        self.request.session['group_id'] = group_id
        self.request.session['member_code'] = member_code
        self.request.session['member_category'] = member_category
        self.request.session['code'] = code
        self.request.session['position'] = position

        return redirect(self.success_url)

    def form_invalid(self, form):
        # Re-populate `group` queryset and `member_code` choices if form is invalid
        center_id = self.request.POST.get('center')
        if center_id:
            form.fields['group'].queryset = GRoup.objects.filter(center_id=center_id)
            try:
                center = Center.objects.get(id=center_id)
                max_member_code = center.no_of_group * center.no_of_members
                form.fields['member_code'].choices = [(i, i) for i in range(1, max_member_code + 1)]
            except Center.DoesNotExist:
                form.fields['member_code'].choices = []
        return super().form_invalid(form)

from django.views.generic.edit import FormView
import json

from .forms import (
    CenterSelectionForm, AddressInformationForm, PersonalInformationForm, FamilyInformationForm, 
    LivestockInformationForm, HouseInformationForm, LandInformationForm, 
    IncomeInformationForm, ExpensesInformationForm
)
from formtools.wizard.views import SessionWizardView

class AddressInfoView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = AddressInformation
    form_class = AddressInformationForm
    template_name = 'member/add_member/address_info.html'
    success_url = reverse_lazy('personal_info')

    def form_valid(self, form):
        # Extract data for all address types
        address_types = ['current', 'permanent', 'old']
        session_data = {}

        for address_type in address_types:
            province = form.cleaned_data.get(f"{address_type}_province").id
            district = form.cleaned_data.get(f"{address_type}_district").id
            municipality = form.cleaned_data.get(f"{address_type}_municipality").id
            ward_no = form.cleaned_data.get(f"{address_type}_ward_no")
            tole = form.cleaned_data.get(f"{address_type}_tole")
            house_no = form.cleaned_data.get(f"{address_type}_house_no")

            # Store data for this address type in session
            session_data[address_type] = {
                'province': province,
                'district': district,
                'municipality': municipality,
                'ward_no': ward_no,
                'tole': tole,
                'house_no': house_no,
            }

            # Print debug information
            print(f"{address_type.capitalize()} Address - Province: {province}, District: {district}, Municipality: {municipality}, Ward: {ward_no}, Tole: {tole}, House: {house_no}")

        # Save all address data into session
        self.request.session['address_info'] = session_data

        # After saving data to session, proceed to the next URL
        return redirect(self.success_url)

    def form_invalid(self, form):
        # Re-populate `district` and `municipality` queryset for all address types if the form is invalid
        address_types = ['current', 'permanent', 'old']

        for address_type in address_types:
            province_id = self.request.POST.get(f"{address_type}_province")
            district_id = self.request.POST.get(f"{address_type}_district")

            if province_id:
                form.fields[f"{address_type}_district"].queryset = District.objects.filter(province_id=province_id)
            else:
                form.fields[f"{address_type}_district"].queryset = District.objects.none()

            if district_id:
                form.fields[f"{address_type}_municipality"].queryset = Municipality.objects.filter(district_id=district_id)
            else:
                form.fields[f"{address_type}_municipality"].queryset = Municipality.objects.none()

        return super().form_invalid(form)

class PersonalInfoView(FormView):
    form_class = PersonalInformationForm
    template_name = 'member/add_member/personal_info.html'

    def get_initial(self):
        """Populate initial data for the form from session."""
        initial_data = self.request.session.get('personal_info', {})

        if 'date_of_birth' in initial_data:
            try:
                # Case 1: If already a `nepali_datetime.date`, leave it as is
                if isinstance(initial_data['date_of_birth'], nepali_datetime.date):
                    pass
                # Case 2: If it's an ISO string, convert it
                elif isinstance(initial_data['date_of_birth'], str):
                    # Parse ISO format string (YYYY-MM-DD)
                    parsed_date = datetime.date.fromisoformat(initial_data['date_of_birth'])
                    # Convert to Nepali date
                    initial_data['date_of_birth'] = nepali_datetime.date.from_datetime_date(parsed_date)
                else:
                    raise ValueError("Unsupported date format.")
            except Exception as e:
                print(f"Error parsing date_of_birth: {e}")
                initial_data['date_of_birth'] = None  # Reset invalid date

        return initial_data

    def form_valid(self, form):
        personal_info = form.cleaned_data

        # Debugging: Print cleaned data
        print("Cleaned data from form:", personal_info)

        # Serialize only the specific fields
        try:
            # Handle date_of_birth (Nepali date)
            if isinstance(personal_info.get('date_of_birth'), nepali_datetime.date):
                personal_info['date_of_birth'] = personal_info['date_of_birth'].isoformat()
            if isinstance(personal_info.get('issued_date'), nepali_datetime.date):
                personal_info['issued_date'] = personal_info['issued_date'].isoformat()

            # Handle registered_by (ForeignKey) -> Ensure always serialized from form
            registered_by = personal_info.get('registered_by', self.request.user)
            if registered_by and hasattr(registered_by, 'pk'):
                personal_info['registered_by'] = registered_by.pk
            else:
                raise ValueError("Registered user is invalid")

        except Exception as e:
            print(f"Serialization error: {e}")
            form.add_error(None, "An error occurred while saving personal information.")
            return self.form_invalid(form)

        # Save the cleaned data to session
        self.request.session['personal_info'] = personal_info
        self.request.session.modified = True

        # Debugging: Check session data
        print("Session data saved:", self.request.session['personal_info'])

        return redirect('family_info')  # Redirect to the next step

    def form_invalid(self, form):
        """Handle invalid forms."""
        return self.render_to_response(self.get_context_data(form=form))


def family_info_view(request):
    if 'personal_info' not in request.session or 'address_info' not in request.session:
        return redirect('address_info')

    request.session['current_step'] = 3
    predefined_relationships = ['Father', 'Husband', 'Father-In-Law']

    # Only create forms for predefined relationships
    forms = [
        FamilyInformationForm(initial={'relationship': rel}, prefix=f'form-{i}')
        for i, rel in enumerate(predefined_relationships)
    ]

    if request.method == 'POST':
        valid = True
        forms = []

        # Validate predefined forms
        for i in range(len(predefined_relationships)):
            form = FamilyInformationForm(request.POST, prefix=f'form-{i}')
            forms.append(form)
            if not form.is_valid():
                valid = False

        # Validate additional forms added dynamically
        i = len(predefined_relationships)
        while f'form-{i}-family_member_name' in request.POST:
            form = FamilyInformationForm(request.POST, prefix=f'form-{i}')
            forms.append(form)
            if not form.is_valid():
                valid = False
            i += 1

        if valid:
            family_info_list = []
            for form in forms:
                form_data = form.cleaned_data.copy()
                for key, value in form_data.items():
                    # Check if the value is a date instance
                    if isinstance(value, date):
                        form_data[key] = value.isoformat()  # Convert to string for JSON compatibility
                family_info_list.append(form_data)

            # Save the serialized data to the session
            request.session['family_info'] = family_info_list
            request.session.modified = True
            return redirect('livestock_info')

    return render(request, 'member/add_member/family_info.html', {'forms': forms})




def livestock_info_view(request):
    if 'address_info' not in request.session or 'personal_info' not in request.session or 'family_info' not in request.session:
        return redirect('address_info')

    request.session['current_step'] = 4
    form = LivestockInformationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        livestock_info = form.cleaned_data
        request.session['livestock_info'] = livestock_info
        return redirect('house_info')

    return render(request, 'member/add_member/livestock_info.html', {'form': form})

def house_info_view(request):
    if 'address_info' not in request.session or 'personal_info' not in request.session or 'family_info' not in request.session or 'livestock_info' not in request.session:
        return redirect('address_info')

    request.session['current_step'] = 5
    form = HouseInformationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        house_info = form.cleaned_data
        request.session['house_info'] = house_info
        return redirect('land_info')

    return render(request, 'member/add_member/house_info.html', {'form': form})

def land_info_view(request):
    if 'address_info' not in request.session or 'personal_info' not in request.session or 'family_info' not in request.session or 'livestock_info' not in request.session or 'house_info' not in request.session:
        return redirect('address_info')

    request.session['current_step'] = 6
    form = LandInformationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        land_info = form.cleaned_data
        request.session['land_info'] = land_info
        return redirect('income_info')

    return render(request, 'member/add_member/land_info.html', {'form': form})

def income_info_view(request):
    if 'address_info' not in request.session or 'personal_info' not in request.session or 'family_info' not in request.session or 'livestock_info' not in request.session or 'house_info' not in request.session or 'land_info' not in request.session:
        return redirect('address_info')

    request.session['current_step'] = 7
    form = IncomeInformationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        income_info = form.cleaned_data
        request.session['income_info'] = income_info
        return redirect('expenses_info')

    return render(request, 'member/add_member/income_info.html', {'form': form})


def expenses_info_view(request):
    required_sessions = [
        'address_info', 'personal_info', 'family_info',
        'livestock_info', 'house_info', 'land_info',
        'income_info', 'expenses_info'
    ]

    if not all(key in request.session for key in required_sessions[:-1]):  # Exclude 'expenses_info'
        return redirect('address_info')

    request.session['current_step'] = 8
    initial_data = request.session.get('expenses_info', {})
    form = ExpensesInformationForm(request.POST or None, initial=initial_data)

    if request.method == 'POST' and form.is_valid():
        expenses_info = form.cleaned_data
        request.session['expenses_info'] = expenses_info

        # Retrieve all session data
        address_info = request.session.get('address_info')
        personal_info = request.session.get('personal_info')
        family_info = request.session.get('family_info')
        livestock_info = request.session.get('livestock_info')
        house_info = request.session.get('house_info')
        land_info = request.session.get('land_info')
        income_info = request.session.get('income_info')

        try:
            with transaction.atomic():
                # Retrieve additional information
                center_id = request.session.get('center_id')
                group_id = request.session.get('group_id')
                member_code = request.session.get('member_code')
                member_category = request.session.get('member_category')
                code = request.session.get('code')
                position = request.session.get('position')

                # Ensure registered_by is valid
                registered_by_id = personal_info.get('registered_by')  # Ensure you're getting the ID
                try:
                    registered_by = User.objects.get(pk=registered_by_id)
                    print(registered_by)
                except User.DoesNotExist:
                    raise ValueError("Invalid registered user ID.")

                print(f'Center_id: {center_id}, Group_id: {group_id}, Member_code: {member_code}, '
                      f'Member_category: {member_category}, Code: {code}, Position: {position}')

                # Create the Member object
                member = Member.objects.create(
                    center_id=center_id,
                    group_id=group_id,
                    member_code=member_code,
                    member_category=member_category,
                    code=code,
                    position=position,
                )

                # Create AddressInformation objects for each type
                for address_type, address_data in zip(['current', 'permanent', 'old'],
                                                       [address_info.get('current', {}),
                                                        address_info.get('permanent', {}),
                                                        address_info.get('old', {})]):
                    AddressInformation.objects.create(
                        member=member,
                        province=Province.objects.get(id=address_data['province']),
                        district=District.objects.get(id=address_data['district']),
                        municipality=Municipality.objects.get(id=address_data['municipality']),
                        ward_no=address_data['ward_no'],
                        tole=address_data['tole'],
                        house_no=address_data['house_no'],
                        address_type=address_type
                    )

                # Create related objects
                personal_info['registered_by'] = registered_by.id  # Ensure it's the User object, not ID
                PersonalInformation.objects.create(member=member, **personal_info)
                FamilyInformation.objects.create(member=member, **family_info)
                LivestockInformation.objects.create(member=member, **livestock_info)
                HouseInformation.objects.create(member=member, **house_info)
                LandInformation.objects.create(member=member, **land_info)
                IncomeInformation.objects.create(member=member, **income_info)
                ExpensesInformation.objects.create(member=member, **expenses_info)

                # Clear session data
                for key in required_sessions:
                    del request.session[key]

            return redirect('member_list')

        except Exception as e:
            print(f"Error creating member: {e}")
            form.add_error(None, "An error occurred while creating the member. Please try again.")

    return render(request, 'member/add_member/expenses_info.html', {'form': form})


# Helper function to get member
def get_member(member_id):
    return get_object_or_404(Member, id=member_id)

# Step 1: Address Information Update
def update_address_info(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    address_info = AddressInformation.objects.filter(member=member)

    if request.method == "POST":
        form = AddressInformationForm(request.POST, instance=address_info.first())
        if form.is_valid():
            # Save current address
            current_address, _ = AddressInformation.objects.update_or_create(
                member=member,
                address_type="current",
                defaults={
                    "province": form.cleaned_data["current_province"],
                    "district": form.cleaned_data["current_district"],
                    "municipality": form.cleaned_data["current_municipality"],
                    "ward_no": form.cleaned_data["current_ward_no"],
                    "tole": form.cleaned_data["current_tole"],
                    "house_no": form.cleaned_data["current_house_no"],
                },
            )

            # Save permanent address
            permanent_address, _ = AddressInformation.objects.update_or_create(
                member=member,
                address_type="permanent",
                defaults={
                    "province": form.cleaned_data["permanent_province"],
                    "district": form.cleaned_data["permanent_district"],
                    "municipality": form.cleaned_data["permanent_municipality"],
                    "ward_no": form.cleaned_data["permanent_ward_no"],
                    "tole": form.cleaned_data["permanent_tole"],
                    "house_no": form.cleaned_data["permanent_house_no"],
                },
            )

            # Save old address (if provided)
            if form.cleaned_data["old_province"]:
                old_address, _ = AddressInformation.objects.update_or_create(
                    member=member,
                    address_type="old",
                    defaults={
                        "province": form.cleaned_data["old_province"],
                        "district": form.cleaned_data["old_district"],
                        "municipality": form.cleaned_data["old_municipality"],
                        "ward_no": form.cleaned_data["old_ward_no"],
                        "tole": form.cleaned_data["old_tole"],
                        "house_no": form.cleaned_data["old_house_no"],
                    },
                )

            messages.success(request, "Address information updated successfully!")
            return redirect("update_personal_info", member_id=member.id)

        else:
            messages.error(request, "Please correct the errors below.")
    else:
        initial_data = {}
        for address_type in ["current", "permanent", "old"]:
            address_instance = address_info.filter(address_type=address_type).first()
            if address_instance:
                initial_data.update({
                    f"{address_type}_province": address_instance.province,
                    f"{address_type}_district": address_instance.district,
                    f"{address_type}_municipality": address_instance.municipality,
                    f"{address_type}_ward_no": address_instance.ward_no,
                    f"{address_type}_tole": address_instance.tole,
                    f"{address_type}_house_no": address_instance.house_no,
                })

        form = AddressInformationForm(initial=initial_data)

    return render(request, "member/update_address_info.html", {
        "form": form,
        "member": member,
    })

# Step 2: Personal Information Update
class UpdatePersonalInfoView(UpdateView):
    model = PersonalInformation
    form_class = PersonalInformationForm
    template_name = 'member/update_personal_info.html'

    def get_object(self):
        """Retrieve the PersonalInformation object for the given member."""
        member_id = self.kwargs.get('member_id')
        return get_object_or_404(PersonalInformation, member_id=member_id)

    def form_valid(self, form):
        # Update the registered_by and registered_date fields
        personal_info = form.save(commit=False)
        personal_info.registered_by = self.request.user
        personal_info.registered_date = nepali_datetime.date.today()  # Assuming Nepali date is needed
        personal_info.save()

        # Redirect to the member detail view with the correct URL argument
        return redirect(reverse('member_detail', kwargs={'member_id': personal_info.member.id}))

    def form_invalid(self, form):
        """Handle invalid forms."""
        return self.render_to_response(self.get_context_data(form=form))


def update_income_info(request, member_id):
    member = get_member(member_id)

    if request.method == 'POST':
        form = IncomeInformationForm(request.POST)
        if form.is_valid():
            request.session['income_info'] = form.cleaned_data
            return redirect('update_expenses_info', member_id=member.id)
    else:
        form = IncomeInformationForm()

    return render(request, 'update_income_info.html', {'form': form, 'member': member})

# Step 4: Expenses Information Update
def update_expenses_info(request, member_id):
    member = get_member(member_id)

    if request.method == 'POST':
        form = ExpensesInformationForm(request.POST)
        if form.is_valid():
            request.session['expenses_info'] = form.cleaned_data
            return redirect('final_update', member_id=member.id)
    else:
        form = ExpensesInformationForm()

    return render(request, 'update_expenses_info.html', {'form': form, 'member': member})

# Final Step: Save all information atomically
def final_update(request, member_id):
    member = get_member(member_id)

    # Retrieve all session data
    address_info = request.session.get('address_info')
    personal_info = request.session.get('personal_info')
    income_info = request.session.get('income_info')
    expenses_info = request.session.get('expenses_info')

    # If any data is missing, redirect back to the first step
    if not address_info or not personal_info or not income_info or not expenses_info:
        messages.error(request, "Please complete all steps first.")
        return redirect('update_address_info', member_id=member.id)

    # Start a transaction block
    try:
        with transaction.atomic():
            # Save address information
            AddressInformation.objects.update_or_create(member=member, defaults=address_info)

            # Save personal information
            PersonalInformation.objects.update_or_create(member=member, defaults=personal_info)

            # Save income information
            IncomeInformation.objects.update_or_create(member=member, defaults=income_info)

            # Save expenses information
            ExpensesInformation.objects.update_or_create(member=member, defaults=expenses_info)

        # Clear session data
        request.session['address_info'] = request.session['personal_info'] = request.session['income_info'] = request.session['expenses_info'] = None

        # Show success message
        messages.success(request, "All member information updated successfully.")
        return redirect('member_detail', member_id=member.id)

    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('update_address_info', member_id=member.id)

FORMS = [
    ("address", AddressInformationForm),
    ("personal", PersonalInformationForm),
    ("family", FamilyInformationForm),
    ("livestock", LivestockInformationForm),
    ("house", HouseInformationForm),
    ("land", LandInformationForm),
    ("income", IncomeInformationForm),
    ("expenses", ExpensesInformationForm),
]

TEMPLATES = {
    "address": "member/add_member/address_info.html",
    "personal": "member/add_member/personal_info.html",
    "family": "member/add_member/family_info.html",
    "livestock": "member/add_member/livestock_info.html",
    "house": "member/add_member/house_info.html",
    "land": "member/add_member/land_info.html",
    "income": "member/add_member/income_info.html",
    "expenses": "member/add_member/expenses_info.html",
}


class MemberWizard(SessionWizardView):
    form_list = FORMS
    predefined_relationships = ["Husband", "Father", "Father-In-Law"]

    def get_template_names(self):
        return [TEMPLATES.get(self.steps.current, "member/add_member/address_info.html")]

    def get_form_initial(self, step):
        if step == "family":
            form_count = sum(1 for key in self.storage.data.get('step_data', {}) if 'family' in key)
            if form_count < len(self.predefined_relationships):
                return {'relationship': self.predefined_relationships[form_count]}
        return super().get_form_initial(step)

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == 'family':
            family_forms = [
                FamilyInformationForm(initial={'relationship': rel}, prefix=f'form-{i}')
                for i, rel in enumerate(self.predefined_relationships)
            ]
            context.update({'family_forms': family_forms, 'form_count': len(family_forms)})
        return context

    def get_form_step_data(self, step):
        data = super().get_form_step_data(step)
        # Convert any date fields to string format
        for key, value in data.items():
            if isinstance(value, date):
                data[key] = value.isoformat()  # Convert date to ISO string
        return data

    def post(self, *args, **kwargs):
        form = self.get_form(data=self.request.POST, files=self.request.FILES)
        if self.steps.current == 'family':
            family_forms = [
                FamilyInformationForm(self.request.POST, prefix=f'form-{i}')
                for i in range(int(self.request.POST.get('form_count', 0)))
            ]

            if self.validate_family_forms(family_forms):
                self.storage.extra_data['family_forms_data'] = [
                    {key: (value.isoformat() if isinstance(value, date) else value) 
                     for key, value in form.cleaned_data.items()}
                    for form in family_forms
                ]
            else:
                return self.render_to_response(
                    self.get_context_data(form=form, family_forms=family_forms)
                )

        return super().post(*args, **kwargs)

    def validate_family_forms(self, family_forms):
        all_valid = True
        for form in family_forms:
            if not form.is_valid():
                all_valid = False
        return all_valid

    def done(self, form_list, **kwargs):
        """This method is called when all the forms are completed successfully."""
        try:
            with transaction.atomic():
                # Retrieve center and group info from the session
                center_id = self.request.session.get('center_id')
                group_id = self.request.session.get('group_id')
                member_code = self.request.session.get('member_code')
                member_category = self.request.session.get('member_category')
                code = self.request.session.get('code')
                position = self.request.session.get('position')
                print(f"{center_id} {group_id} {member_code} {member_category} {code} {position}")

                # Create the Member object now that we have all necessary information
                member = Member.objects.create(
                    center_id=center_id,
                    group_id=group_id,
                    member_code=member_code,
                    member_category=member_category,
                    code=code,
                    position=position,
                )

                # Save each form's data linked to this new Member
                for form in form_list:
                    form_instance = form.save(commit=False)  # Don't commit yet
                    form_instance.member = member  # Link form data to the member
                    form_instance.save()  # Save the form instance data

                messages.success(self.request, "Member created successfully.")

                # Clear session data after creating member
                self.request.session.pop('center_id', None)
                self.request.session.pop('group_id', None)
                self.request.session.pop('member_code', None)
                self.request.session.pop('member_category', None)
                self.request.session.pop('code', None)
                self.request.session.pop('position', None)
                return redirect('member_list') 
        except Exception as e:
            # Handle exception if saving fails
            messages.error(self.request, f"Error saving member: {e}")
            return redirect('member_list')

def load_groups(request):
    center_id = request.GET.get('center')
    groups = GRoup.objects.filter(center_id=center_id).values('id', 'name', 'code')
    return JsonResponse(list(groups), safe=False)

def load_member_codes(request):
    center_id = request.GET.get('center')
    try:
        center = Center.objects.get(id=center_id)
        max_member_code = center.no_of_group * center.no_of_members
        member_codes = list(range(1, max_member_code + 1))
    except Center.DoesNotExist:
        member_codes = []
    
    return JsonResponse(member_codes, safe=False)


   
class MemberDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Member
    success_url = reverse_lazy('member_list')
    template_name = 'member/delete_member.html'
    
FORMSS = [
    ("personal", PersonalInformationForm),
    ("address", AddressInformationForm),
    ("family", FamilyInformationForm),
    ("livestock", LivestockInformationForm),
    ("house", HouseInformationForm),
    ("land", LandInformationForm),
    ("income", IncomeInformationForm),
    ("expenses", ExpensesInformationForm),
]

TEMPLATES = {
    "personal": "member/update_member/personal_info.html",
    "address": "member/update_member/address_info.html",
    "family": "member/update_member/family_info.html",
    "livestock": "member/update_member/livestock_info.html",
    "house": "member/update_member/house_info.html",
    "land": "member/update_member/land_info.html",
    "income": "member/update_member/income_info.html",
    "expenses": "member/update_member/expenses_info.html",
}
class MemberUpdateWizard(LoginRequiredMixin, RoleRequiredMixin, SessionWizardView):
    """
    View for updating member information across multiple steps
    """
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_form_initial(self, step):
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(Member, pk=member_id)
        
        # Fetch related models for the member
        personal_info = get_object_or_404(PersonalInformation, member=member)
        address_info = get_object_or_404(AddressInformation, member=member)
        family_info = get_object_or_404(FamilyInformation, member=member)
        livestock_info = get_object_or_404(LivestockInformation, member=member)
        house_info = get_object_or_404(HouseInformation, member=member)
        land_info = get_object_or_404(LandInformation, member=member)
        income_info = get_object_or_404(IncomeInformation, member=member)
        expenses_info = get_object_or_404(ExpensesInformation, member=member)

        initial = super().get_form_initial(step)

        if step == "personal":
            initial.update({
                'first_name': personal_info.first_name,
                'middle_name': personal_info.middle_name,
                'last_name': personal_info.last_name,
                'phone_number': personal_info.phone_number,
                'gender': personal_info.gender,
                'marital_status': personal_info.marital_status,
                'family_status': personal_info.family_status,
                'education': personal_info.education,
                'religion': personal_info.religion,
                'occupation': personal_info.occupation,
                'family_member_no': personal_info.family_member_no,
                'date_of_birth': personal_info.date_of_birth,
                'voter_id': personal_info.voter_id,
                'voter_id_issued_on': personal_info.voter_id_issued_on,
                'citizenship_no': personal_info.citizenship_no,
                'issued_from': personal_info.issued_from,
                'issued_date': personal_info.issued_date,
                'marriage_reg_no': personal_info.marriage_reg_no,
                'registered_vdc': personal_info.registered_vdc,
                'marriage_regd_date': personal_info.marriage_regd_date,
                'file_no': personal_info.file_no,
            })
        elif step == "address":
            initial.update({
                'permanent_province': address_info.permanent_province,
                'permanent_district': address_info.permanent_district,
                'permanent_municipality': address_info.permanent_municipality,
                'permanent_ward_no': address_info.permanent_ward_no,
                'permanent_tole': address_info.permanent_tole,
                'permanent_house_no': address_info.permanent_house_no,
                'current_province': address_info.current_province,
                'current_district': address_info.current_district,
                'current_municipality': address_info.current_municipality,
                'current_ward_no': address_info.current_ward_no,
                'current_tole': address_info.current_tole,
                'current_house_no': address_info.current_house_no,
                'old_province': address_info.old_province,
                'old_district': address_info.old_district,
                'old_municipality': address_info.old_municipality,
                'old_ward_no': address_info.old_ward_no,
                'old_tole': address_info.old_tole,
                'old_house_no': address_info.old_house_no,
            })
        elif step == "family":
            initial.update({
                'family_member_name': family_info.family_member_name,
                'relationship': family_info.relationship,
                'date_of_birth': family_info.date_of_birth,
                'citizenship_no': family_info.citizenship_no,
                'issued_from': family_info.issued_from,
                'issued_date': family_info.issued_date,
                'education': family_info.education,
                'occupation': family_info.occupation,
                'monthly_income': family_info.monthly_income,
                'phone_number': family_info.phone_number,
            })
        elif step == "livestock":
            initial.update({
                'cows': livestock_info.cows,
                'buffalo': livestock_info.buffalo,
                'goat': livestock_info.goat,
                'sheep': livestock_info.sheep,
            })
        elif step == "house":
            initial.update({
                'concrete': house_info.concrete,
                'mud': house_info.mud,
                'iron': house_info.iron,
            })
        elif step == "land":
            initial.update({
                'farming_land': land_info.farming_land,
                'other_land': land_info.other_land,
            })
        elif step == "income":
            initial.update({
                'agriculture_income': income_info.agriculture_income,
                'animal_farming_income': income_info.animal_farming_income,
                'business_income': income_info.business_income,
                'abroad_employment_income': income_info.abroad_employment_income,
                'wages_income': income_info.wages_income,
                'personal_job_income': income_info.personal_job_income,
                'government_post': income_info.government_post,
                'pension': income_info.pension,
                'other': income_info.other,
            })
        elif step == "expenses":
            initial.update({
                'house_expenses': expenses_info.house_expenses,
                'education_expenses': expenses_info.education_expenses,
                'health_expenses': expenses_info.health_expenses,
                'festival_expenses': expenses_info.festival_expenses,
                'clothes_expenses': expenses_info.clothes_expenses,
                'communication_expenses': expenses_info.communication_expenses,
                'fuel_expenses': expenses_info.fuel_expenses,
                'entertaiment_expenses': expenses_info.entertaiment_expenses,
                'other_expenses': expenses_info.other_expenses,
            })

        return initial

    def done(self, form_list, **kwargs):
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(Member, pk=member_id)

        with transaction.atomic():
            for form in form_list:
                form_instance = form.save(commit=False)
                
                if isinstance(form_instance, PersonalInformation):
                    personal_info, created = PersonalInformation.objects.update_or_create(
                        member=member,
                        defaults={
                            'first_name': form_instance.first_name,
                            'middle_name': form_instance.middle_name,
                            'last_name': form_instance.last_name,
                            'phone_number': form_instance.phone_number,
                            'gender': form_instance.gender,
                            'marital_status': form_instance.marital_status,
                            'family_status': form_instance.family_status,
                            'education': form_instance.education,
                            'religion': form_instance.religion,
                            'occupation': form_instance.occupation,
                            'family_member_no': form_instance.family_member_no,
                            'date_of_birth': form_instance.date_of_birth,
                            'voter_id': form_instance.voter_id,
                            'voter_id_issued_on': form_instance.voter_id_issued_on,
                            'citizenship_no': form_instance.citizenship_no,
                            'issued_from': form_instance.issued_from,
                            'issued_date': form_instance.issued_date,
                            'marriage_reg_no': form_instance.marriage_reg_no,
                            'registered_vdc': form_instance.registered_vdc,
                            'marriage_regd_date': form_instance.marriage_regd_date,
                            'file_no': form_instance.file_no,
                        }
                    )
                elif isinstance(form_instance, AddressInformation):
                    AddressInformation.objects.update_or_create(
                        member=member,
                        defaults={
                            'permanent_province': form_instance.permanent_province,
                            'permanent_district': form_instance.permanent_district,
                            'permanent_municipality': form_instance.permanent_municipality,
                            'permanent_ward_no': form_instance.permanent_ward_no,
                            'permanent_tole': form_instance.permanent_tole,
                            'permanent_house_no': form_instance.permanent_house_no,
                            'current_district': form_instance.current_district,
                            'current_municipality': form_instance.current_municipality,
                            'current_province': form_instance.current_province,
                            'current_ward_no': form_instance.current_ward_no,
                            'current_tole': form_instance.current_tole,
                            'current_house_no': form_instance.current_house_no,
                            'old_province': form_instance.old_province,
                            'old_district': form_instance.old_district,
                            'old_municipality': form_instance.old_municipality,
                            'old_ward_no': form_instance.old_ward_no,
                            'old_tole': form_instance.old_tole,
                            'old_house_no': form_instance.old_house_no,
                        }
                    )
                elif isinstance(form_instance, FamilyInformation):
                    FamilyInformation.objects.update_or_create(
                        member=member,
                        defaults={
                            'family_member_name': form_instance.family_member_name,
                            'relationship': form_instance.relationship,
                            'date_of_birth': form_instance.date_of_birth,
                            'citizenship_no': form_instance.citizenship_no,
                            'issued_from': form_instance.issued_from,
                            'issued_date': form_instance.issued_date,
                            'education': form_instance.education,
                            'occupation': form_instance.occupation,
                            'monthly_income': form_instance.monthly_income,
                            'phone_number': form_instance.phone_number,
                        }
                    )
                elif isinstance(form_instance, LivestockInformation):
                    LivestockInformation.objects.update_or_create(
                        member=member,
                        defaults={
                            'cows': form_instance.cows,
                            'buffalo': form_instance.buffalo,
                            'goat': form_instance.goat,
                            'sheep': form_instance.sheep,
                        }
                    )
                elif isinstance(form_instance, HouseInformation):
                    HouseInformation.objects.update_or_create(
                        member=member,
                        defaults={
                            'concrete': form_instance.concrete,
                            'mud': form_instance.mud,
                            'iron': form_instance.iron,
                        }
                    )
                elif isinstance(form_instance, LandInformation):
                    LandInformation.objects.update_or_create(
                        member=member,
                        defaults={
                            'farming_land': form_instance.farming_land,
                            'other_land': form_instance.other_land,
                        }
                    )
                elif isinstance(form_instance, IncomeInformation):
                    IncomeInformation.objects.update_or_create(
                        member=member,
                        defaults={
                            'agriculture_income': form_instance.agriculture_income,
                            'animal_farming_income': form_instance.animal_farming_income,
                            'business_income': form_instance.business_income,
                            'abroad_employment_income': form_instance.abroad_employment_income,
                            'wages_income': form_instance.wages_income,
                            'personal_job_income': form_instance.personal_job_income,
                            'government_post': form_instance.government_post,
                            'pension': form_instance.pension,
                            'other': form_instance.other,
                        }
                    )
                elif isinstance(form_instance, ExpensesInformation):
                    ExpensesInformation.objects.update_or_create(
                        member=member,
                        defaults={
                            'house_expenses': form_instance.house_expenses,
                            'education_expenses': form_instance.education_expenses,
                            'health_expenses': form_instance.health_expenses,
                            'festival_expenses': form_instance.festival_expenses,
                            'clothes_expenses': form_instance.clothes_expenses,
                            'communication_expenses': form_instance.communication_expenses,
                            'fuel_expenses': form_instance.fuel_expenses,
                            'entertaiment_expenses': form_instance.entertaiment_expenses,
                            'other_expenses': form_instance.other_expenses,
                        }
                    )

        return redirect('member_detail', member_id = member.id)


def member_detail_view(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    personal_info = member.personalInfo
    address_info = member.address_info.filter(address_type='current').first()
    print(address_info)
    family_info = FamilyInformation.objects.filter(member=member).all()
    livestock_info = member.livestockInfo
    house_info = member.houseInfo
    land_info = member.landInfo
    income_info = member.incomeInfo
    expenses_info = member.expensesInfo
    savings_accounts = SavingsAccount.objects.filter(member=member).all()
    loans = member.loans.all()
    
    context = {
        'member': member,
        'personal_info': personal_info,
        'address_info': address_info,
        'family_info': family_info,
        'livestock_info': livestock_info,
        'house_info': house_info,
        'land_info': land_info,
        'income_info': income_info,
        'expenses_info': expenses_info,
        'savings_accounts': savings_accounts,
        'loans': loans,
    }
    
    return render(request, 'member/member_detail.html', context)

def get_saving_accounts(request, member_id):
    accounts = SavingsAccount.objects.filter(member_id=member_id).values('account_type', 'account_number', 'balance')
    account_data = []

    for account in accounts:
        statements = Statement.objects.filter(account__account_number=account['account_number'])
        total_credit = statements.get_total_cr_amount()
        total_debit = statements.get_total_dr_amount()

        account_data.append({
            'account_type': account['account_type'],
            'account_number': account['account_number'],
            'balance': account['balance'],
            'total_credit': total_credit,
            'total_debit': total_debit,
        })
    return JsonResponse({'accounts': account_data})

from django.db.models import Prefetch
class MemberListView(ListView):
    model = Member
    template_name = 'member/member_list.html'
    context_object_name = 'members'

    # Pass the MEMBER_STATUS choices to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['member_status'] = Member.MEMBER_STATUS 
        return context


    def get_queryset(self):
        # Prefetch only current addresses
        current_address_prefetch = Prefetch(
            'address_info', 
            queryset=AddressInformation.objects.filter(address_type='current'),
            to_attr='current_address'
        )
        queryset = Member.objects.all().select_related('personalInfo').prefetch_related(current_address_prefetch).filter(status='A')
        status_filter = self.request.GET.get('status')
        # Ensure the filter value is one of the valid status codes
        valid_status_codes = [code for code, label in Member.MEMBER_STATUS]
        if status_filter in valid_status_codes:
           queryset = Member.objects.all().select_related('personalInfo').filter(status__iexact=status_filter)
        return queryset
    
def change_member_status(request):
    if request.method == 'POST':
        member_id = request.POST.get('memberId')
        new_status = request.POST.get('status')

        member = get_object_or_404(Member, id=member_id)
        member.status = new_status 
        member.save() 

       # Check if the accounts should be created automatically
        if request.POST.get('create_accounts') == 'yes':
            # Loop through each account type and create them for the member
            for account_code, account_name in INITIAL_SAVING_ACCOUNT_TYPE:
                SavingsAccount.objects.create(
                    member=member,
                    account_type=account_code,
                    account_number=f"{member.code}.{account_code}.1", 
                    balance=0.00 ,
                )
            
        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)


@login_required
def branch_list_view(request):
    branches = Branch.objects.all()
    return render(request, "branch/branch_list.html",{
        'branches': branches
    })


@login_required
def employee_list_view(request):
    employees = Employee.objects.all().select_related('user')
    return render(request, 'employee/employee_list.html', {
        'employees': employees
    })



def deposits(request):
    return render(request, 'dashboard/deposits.html')

def transactions(request):
    return render(request, 'dashboard/transactions.html')

def reports(request):
    return render(request, 'dashboard/reports.html')