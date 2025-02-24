from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from decimal import Decimal

import nepali_datetime
from django.db import transaction
from django.db.models import Count, Avg

from django.views.generic import (
    CreateView, ListView, UpdateView, DeleteView )

from dashboard.models import (Province, District, Municipality, 
                              Branch, Employee, GRoup, Center,
                              Member, AddressInformation, 
                              PersonalInformation, PersonalMemberDocument, 
                              FamilyInformation, FamilyMemberDocument,  
                              LivestockInformation, HouseInformation, LandInformation, 
                              IncomeInformation, ExpensesInformation)
from savings.models import SavingsAccount, INITIAL_SAVING_ACCOUNT_TYPE, Statement
from core.models import Teller, Voucher

from dashboard.forms import (BranchForm, EmployeeForm, CenterForm, GroupForm, 
                             PersonalMemberDocumentForm)

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
    branch = request.user.employee_detail.branch
    members =Member.objects.all().select_related('personalInfo')
    address_info= None
    try:
        for member in members:
            address_info = member.address_info.filter(address_type='current').first()
    except:
        address_info = 'No Address Found!'
    groups = GRoup.objects.all()
    centers = Center.objects.all()
    employees = Employee.objects.all()

    #Member Summary
    total_centers = Center.objects.filter(branch=branch).distinct().count()
    active_members = members.filter(center__branch=branch, status="A").count()
    droupout_members = members.filter(center__branch=branch, status="D").count()
    loanee_members = members.filter(center__branch=branch, status="A", loans__isnull=False).count()
  # Query to count all members in each center for the given branch
    members_per_center = members.filter(center__branch=branch).values('center').annotate(member_count=Count('id'))
    # Calculate the total number of members across all centers
    total_members = sum(item['member_count'] for item in members_per_center)

    # Calculate the average number of members per center
    average_members_per_center = round(total_members / total_centers, 2) if total_centers else 0


    return render(request, "dashboard/admin_dashboard.html",{
        'bank': 'Admin',
        'groups': groups,
        'centers': centers,
        'employees': employees,
        'members': members,
        'address_info': address_info,
        'total_centers': total_centers,
        'active_members': active_members,
        'droupout_members': droupout_members,
        'loanee_members': loanee_members,
        'average_members_per_center': average_members_per_center,
    })

@login_required
def manager_dashboard(request):
    branch = request.user.employee_detail.branch
    members =Member.objects.filter(center__branch=branch).select_related('personalInfo')
    address_info= None
    try:
        for member in members:
            address_info = member.address_info.filter(address_type='current').first()
    except:
        address_info = 'No Address Found!'
    groups = GRoup.objects.filter(center__branch=branch).all()
    centers = Center.objects.filter(branch=branch).all()
    employees = Employee.objects.filter(branch=branch).all()

    #Member Summary
    total_centers = Center.objects.filter(branch=branch).distinct().count()
    active_members = members.filter(center__branch=branch, status="A").count()
    droupout_members = members.filter(center__branch=branch, status="D").count()
    loanee_members = members.filter(center__branch=branch, status="A", loans__isnull=False).count()
  # Query to count all members in each center for the given branch
    members_per_center = members.filter(center__branch=branch).values('center').annotate(member_count=Count('id'))
    # Calculate the total number of members across all centers
    total_members = sum(item['member_count'] for item in members_per_center)

    # Calculate the average number of members per center
    average_members_per_center = round(total_members / total_centers, 2) if total_centers else 0

    return render(request, "dashboard/manager_dashboard.html",{
        'branch': branch,
        'bank': 'Manager',
        'groups': groups,
        'centers': centers,
        'employees': employees,
        'members': members,
        'address_info': address_info,
        'total_centers': total_centers,
        'active_members': active_members,
        'droupout_members': droupout_members,
        'loanee_members': loanee_members,
        'average_members_per_center': average_members_per_center,
    })

@login_required
def employee_dashboard(request):
    branch = request.user.employee_detail.branch
    members =Member.objects.filter(center__branch=branch).select_related('personalInfo')
    address_info= None
    try:
        for member in members:
            address_info = member.address_info.filter(address_type='current').first()
    except:
        address_info = 'No Address Found!'
    groups = GRoup.objects.filter(center__branch=branch).all()
    centers = Center.objects.filter(branch=branch).all()
    employees = Employee.objects.filter(branch=branch).all()

    #Member Summary
    total_centers = Center.objects.filter(branch=branch).distinct().count()
    active_members = members.filter(center__branch=branch, status="A").count()
    droupout_members = members.filter(center__branch=branch, status="D").count()
    loanee_members = members.filter(center__branch=branch, status="A", loans__isnull=False).count()
  # Query to count all members in each center for the given branch
    members_per_center = members.filter(center__branch=branch).values('center').annotate(member_count=Count('id'))
    # Calculate the total number of members across all centers
    total_members = sum(item['member_count'] for item in members_per_center)

    # Calculate the average number of members per center
    average_members_per_center = round(total_members / total_centers, 2) if total_centers else 0

    
    return render(request, "dashboard/employee_dashboard.html",{
        'branch': branch,
        'bank': 'Staff',
        'groups': groups,
        'centers': centers,
        'employees': employees,
        'members': members,
        'address_info': address_info,
        'total_centers': total_centers,
        'active_members': active_members,
        'droupout_members': droupout_members,
        'loanee_members': loanee_members,
        'average_members_per_center': average_members_per_center,
    })


## BRANCH ##
class BranchCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Branch
    form_class = BranchForm
    template_name = 'branch/add_branch.html'
    success_url = reverse_lazy('branch_list')

    def form_valid(self, form):
        messages.success(self.request, 'Branch created successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
    
@login_required
def branch_list_view(request):
    branches = Branch.objects.all().order_by('id')
    paginator = Paginator(branches, 10)  # Show 10 centers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # managers = {}
    # for branch in branches:
    #     manager = Employee.objects.filter(branch=branch, role='manager').first()
    #     managers = branch.id[manager]
    managers = {branch.id: Employee.objects.filter(branch=branch, role='manager').all() for branch in branches}
    return render(request, 'branch/branch_list.html', {'branches': page_obj, 'managers': managers})

class BranchUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Branch
    form_class = BranchForm
    template_name = 'branch/update_branch.html'
    success_url = reverse_lazy('branch_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Branch updated successfully!")
        return super().form_valid(form)

class BranchDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Branch
    success_url = reverse_lazy('branch_list')
    template_name = 'branch/delete_branch.html'

    def form_valid(self, form):
        messages.error(self.request, "Branch deleted successfully!")
        return super().form_valid(form)


## EMPLOYEE ##
class EmployeeListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Employee
    template_name = 'employee/employee_list.html'
    context_object_name = 'employees'

    def get_queryset(self):
        branch = self.request.user.employee_detail.branch
        user_role = self.request.user.employee_detail.role
        if user_role =='admin':
            queryset = Employee.objects.all().order_by('name')
        elif user_role =='manager' or user_role == 'staff':
            queryset = Employee.objects.filter(branch=branch).order_by('name')
        else:
            PermissionDenied
        paginator = Paginator(queryset, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return page_obj


class EmployeeCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee/add_employee.html'
    success_url = reverse_lazy('employee_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Set the user who created the center
        cleaned_data = form.cleaned_data
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
        messages.success(self.request, 'Employee added successfully!')
        return super().form_valid(form)
    

    def form_invalid(self, form):
        # messages.error(self.request, f'Error adding employee: {form.errors}')
        return super().form_invalid(form)
    
class EmployeeUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee/edit_employee.html'
    success_url = reverse_lazy('employee_list')

    def get_form_kwargs(self):
        kwargs =  super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, "Employee details updated successfully!")
        return super().form_valid(form)

    
class EmployeeDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Employee
    success_url = reverse_lazy('employee_list')
    template_name = 'employee/delete_employee.html'

    def form_valid(self, form):
        messages.error(self.request, "Employee deleted successfully!")
        return super().form_valid(form)

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
            messages.success(request, 'Employee added successfully!')
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

    def get_queryset(self):
        branch = self.request.user.employee_detail.branch
        user_role = self.request.user.employee_detail.role
        if user_role == 'admin':
            queryset = Center.objects.all().order_by('formed_date')
        elif user_role =='manager' or user_role =='employee':
            queryset = Center.objects.filter(branch=branch).all().order_by('formed_date')
        else:
            raise PermissionDenied
        paginator = Paginator(queryset, 10)  # 10 centers per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return page_obj

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
    
    def form_valid(self, form):
        messages.success(self.request, "Center updated successfully!")
        return super().form_valid(form)

class CenterDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Center
    success_url = reverse_lazy('center_list')
    template_name = 'center/delete_center.html'

    def form_valid(self, form):
        messages.error(self.request, "Center deleted successfully!")
        return super().form_valid(form)


## GROUPS ##
class GroupListView(LoginRequiredMixin, ListView):
    model = GRoup
    context_object_name = 'groups'
    template_name = 'group/group_list.html'

    def get_queryset(self):
        branch = self.request.user.employee_detail.branch
        user_role = self.request.user.employee_detail.role
        if user_role == 'admin':
            queryset = GRoup.objects.all().order_by('-created_on')
        elif user_role == 'manager' or user_role == 'employee':
            queryset = GRoup.objects.filter(center__branch=branch).all().order_by('-created_on')
        else:
            raise PermissionDenied
        paginator = Paginator(queryset, 10)  # 10 centers per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return page_obj

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

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

    def form_valid(self, form):
        messages.success(self.request, "Group updated successfully!")
        return super().form_valid(form)

class GroupDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = GRoup
    success_url = reverse_lazy('group_list')
    template_name = 'group/delete_group.html'

    def form_valid(self, form):
        messages.warning(self.request, "Group deleted successfully!")
        return super().form_valid(form)


## MEMBERS ##
from .forms import CenterSelectionForm
class SelectCenterView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Member
    form_class = CenterSelectionForm
    # template_name = 'dashboard/select_center.html'
    template_name = 'member/add_member/select_center.html'
    success_url = reverse_lazy('address_info') 

    def dispatch(self, request, *args, **kwargs):
        """Delete any unfinished members before starting a new process."""
        Member.objects.filter(temporary=True).delete()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Store center and group information in the session instead of saving the Member
        center_id = form.cleaned_data['center'].id
        group_id = form.cleaned_data['group'].id
        member_code = form.cleaned_data['member_code']
        member_category = form.cleaned_data['member_category']
        code = form.cleaned_data['code']
        position = form.cleaned_data['position']
        print(f"{center_id} {group_id} {member_code} {member_category} {code} {position}")

        # Create and save the Member instance
        member = Member.objects.create(
            center_id=center_id,
            group_id=group_id,
            member_code=member_code,
            member_category=member_category,
            code=code,
            position=position,
            temporary=True,  # Mark as temporary
        )
        
        # Store these details in the session
        self.request.session['member_id'] = member.id
        # self.request.session['group_id'] = group_id
        # self.request.session['member_code'] = member_code
        # self.request.session['member_category'] = member_category
        # self.request.session['code'] = code
        # self.request.session['position'] = position

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

from .forms import (
    CenterSelectionForm, AddressInformationForm, PersonalInformationForm, FamilyInformationForm, 
    LivestockInformationForm, HouseInformationForm, LandInformationForm, 
    IncomeInformationForm, ExpensesInformationForm
)

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
            # print(f"{address_type.capitalize()} Address - Province: {province}, District: {district}, Municipality: {municipality}, Ward: {ward_no}, Tole: {tole}, House: {house_no}")
            print(self.request.session.get('member_id'))

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve the member object
        member_id = self.request.session.get('member_id')
        member = get_object_or_404(Member, id=member_id)
        # Pass the member instance to the context
        personal_documents = member.personal_documents.all() or []
        context['member'] = member
        context['document_form'] = PersonalMemberDocumentForm()
        context['personal_documents'] = personal_documents
        return context

    def get_initial(self):
        """Populate initial data for the form from session."""
        return self.request.session.get('personal_info', {}) or {}

    def form_valid(self, form):
        personal_info = form.cleaned_data
        # Serialize only the specific fields
        try:
            # Handle date_of_birth (Nepali date)
            if isinstance(personal_info.get('date_of_birth'), nepali_datetime.date):
                personal_info['date_of_birth'] = personal_info['date_of_birth'].isoformat()
            if isinstance(personal_info.get('issued_date'), nepali_datetime.date):
                personal_info['issued_date'] = personal_info['issued_date'].isoformat()
            if isinstance(personal_info.get('voter_id_issued_on'), nepali_datetime.date):
                personal_info['voter_id_issued_on'] = personal_info['voter_id_issued_on'].isoformat()
            if isinstance(personal_info.get('marriage_regd_date'), nepali_datetime.date):
                personal_info['marriage_regd_date'] = personal_info['marriage_regd_date'].isoformat()
            if isinstance(personal_info.get('registered_date'), nepali_datetime.date):
                personal_info['registered_date'] = personal_info['registered_date'].isoformat()

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
        # print("Session data saved:", self.request.session['personal_info'])

        return redirect('family_info')  # Redirect to the next step

    def form_invalid(self, form):
        """Handle invalid forms."""
        return self.render_to_response(self.get_context_data(form=form))

class FamilyInfoView(FormView):
    template_name = "member/add_member/family_info.html"
    form_class = FamilyInformationForm

    def get_predefined_relationships(self):
        """Determine predefined relationships based on personal info."""
        personal_info = self.request.session.get("personal_info", {})
        gender = personal_info.get("gender")
        marital_status = personal_info.get("marital_status")

        if gender == "Male" or (gender == "Female" and marital_status == "Single"):
            return ["Grandfather", "Father", "Mother"]
        return ["Father", "Husband", "Father-In-Law"]

    def get_initial(self):
        """Populate initial data for the forms from session if available."""
        family_info = self.request.session.get("family_info", [])
        predefined_relationships = self.get_predefined_relationships()

        initial_data = {}
        for i, rel in enumerate(predefined_relationships):
            if i < len(family_info):
                initial_data[f"form-{i}"] = {**family_info[i], "relationship": rel}
            else:
                initial_data[f"form-{i}"] = {"relationship": rel}
        return initial_data

    def get(self, request, *args, **kwargs):
        """Handle GET requests to display initial forms."""
        if "personal_info" not in request.session or "address_info" not in request.session:
            return redirect("address_info")
        
        request.session["current_step"] = 3
        initial_data = self.get_initial()
        predefined_relationships = self.get_predefined_relationships()

        # Create forms for predefined relationships
        forms = [
            FamilyInformationForm(initial=initial_data.get(f"form-{i}", {}), prefix=f"form-{i}")
            for i in range(len(predefined_relationships))
        ]

        return self.render_to_response({"forms": forms})

    def process_forms(self, request):
        """Process forms submitted via POST."""
        predefined_relationships = self.get_predefined_relationships()
        forms = []
        valid = True

        # Validate predefined forms
        for i in range(len(predefined_relationships)):
            form = FamilyInformationForm(request.POST, prefix=f"form-{i}")
            forms.append(form)
            if not form.is_valid():
                valid = False

        # Validate additional forms dynamically
        prefixes = [
            key.rsplit("-", 1)[0]
            for key in request.POST.keys()
            if "-family_member_name" in key
        ]

        prefixes = sorted(set(prefixes), key=lambda x: int(x.split("-")[1]))  # Ensure correct order

        for prefix in prefixes:
            if prefix not in [f"form-{i}" for i in range(len(predefined_relationships))]:
                form = FamilyInformationForm(request.POST, prefix=prefix)
                forms.append(form)
                if not form.is_valid():
                    valid = False

        # print("Extracted prefixes:", prefixes)
        return forms, valid

    def post(self, request, *args, **kwargs):
        """Handle POST requests for form submission."""
        forms, valid = self.process_forms(request)
        # print(forms)
        # print(request.POST)
        if valid:
            family_info_list = []
            for form in forms:
                form_data = form.cleaned_data.copy()

                # Serialize Nepali dates
                for key, value in form_data.items():
                    if isinstance(value, (date, nepali_datetime.date)):
                        form_data[key] = value.isoformat()

                family_info_list.append(form_data)

            # Save to session
            request.session["family_info"] = family_info_list
            request.session.modified = True
            return redirect("livestock_info")

        return self.render_to_response({"forms": forms})

    def render_to_response(self, context, **response_kwargs):
        """Ensure proper context rendering."""
        response_kwargs.setdefault("content_type", self.content_type)
        return super().render_to_response(context, **response_kwargs)


from django.template.loader import render_to_string
def get_new_family_form(request):
    """
    AJAX view to dynamically add a new family member form.
    """
    try:
        existing_count = int(request.GET.get('count', 0))
    except ValueError:
        return JsonResponse({'error': 'Invalid count'}, status=400)

    new_form = FamilyInformationForm(prefix=f'family-{existing_count}')
    form_html = render_to_string('member/add_member/family_info_form.html', {'form': new_form})
    return JsonResponse({'form_html': form_html})


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
                member_id = request.session.get('member_id')
                member = Member.objects.get(id=member_id)
                
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
                if 'registered_by' in personal_info:
                    del personal_info['registered_by']

                user = request.user
                PersonalInformation.objects.create(
                    member=member,
                    registered_by=user,
                    **personal_info
                )
                for family_data in family_info:
                    FamilyInformation.objects.create(member=member, **family_data)
                LivestockInformation.objects.create(member=member, **livestock_info)
                HouseInformation.objects.create(member=member, **house_info)
                LandInformation.objects.create(member=member, **land_info)
                IncomeInformation.objects.create(member=member, **income_info)
                ExpensesInformation.objects.create(member=member, **expenses_info)

                if member_id:
                  Member.objects.filter(id=member_id).update(temporary=False)
    
                # Clear session data
                for key in required_sessions:
                    del request.session[key]
            messages.success(request, "Member created successfully.")        
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

    return render(request, "member/add_member/address_info.html", {
        "form": form,
        "member": member,
    })

def upload_document(request):
    if request.method == "POST":
        form = PersonalMemberDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                member = Member.objects.get(id=request.POST.get('member'))
            except Member.DoesNotExist:
                return JsonResponse({"success": False, "message": "Member not found"}, status=400)

            doc = form.save(commit=False)
            doc.member = member
            doc.uploaded_by = request.user
            doc.save()
            return JsonResponse({
                "success": True,
                "document": {
                    "id": doc.id,
                    "document_type": doc.document_type,
                    "document_file_url": doc.document_file.url,
                    "document_file_name": doc.document_file.name.split("/member/personal/")[-1],  # Extract filename
                }
            }, status=200)  

        return JsonResponse({"success": False, "errors": form.errors})
    
    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)

def delete_document(request, document_id):
    if request.method == "DELETE":
        document = get_object_or_404(PersonalMemberDocument, id=document_id)
        document.delete()
        return JsonResponse({"success": True, "message": "Document deleted successfully."})
    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)


# Step 2: Personal Information Update
class UpdatePersonalInfoView(UpdateView):
    model = PersonalInformation
    form_class = PersonalInformationForm
    template_name = 'member/add_member/personal_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve the member object
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(Member, id=member_id)
        # Pass the member instance to the context
        personal_documents = member.personal_documents.all() or []
        context['member'] = member
        context['document_form'] = PersonalMemberDocumentForm()
        context['personal_documents'] = personal_documents
        return context

    def get_object(self):
        """Retrieve the PersonalInformation object for the given member."""
        member_id = self.kwargs.get('member_id')
        return get_object_or_404(PersonalInformation, member_id=member_id)

    def form_valid(self, form):
        # Update the registered_by and registered_date fields
        personal_info = form.save(commit=False)
        personal_info.registered_by = self.request.user
        personal_info.registered_date = nepali_datetime.date.today()  # Assuming Nepali date is needed
        member_id = self.object.member_id
        personal_info.save()
        messages.success(self.request, "Personal information updated successfully!")
        # Redirect to the member detail view with the correct URL argument
        return redirect(reverse('update_family_info', kwargs={'member_id': member_id}))

    def form_invalid(self, form):
        """Handle invalid forms."""
        return self.render_to_response(self.get_context_data(form=form))

class UpdateFamilyInfoView(FormView):
    template_name = "member/add_member/family_info.html"  # Use the same template as FamilyInfoView
    form_class = FamilyInformationForm

    def get_initial(self):
        """Populate initial data for the forms from existing family info."""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(Member, id=member_id)

        # Fetch all existing FamilyInformation for the member
        existing_family_info = FamilyInformation.objects.filter(member=member)

        # Initialize forms for both existing and dynamic family members
        forms = []
        for i, instance in enumerate(existing_family_info):
            form = FamilyInformationForm(instance=instance, prefix=f'family-{i}')
            forms.append(form)

        # Prepare context for dynamic form (add more family members)
        return {
            'member': member,
            'forms': forms,
        }

    def form_valid(self, form):
        """Process the form data on valid submission."""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(Member, id=member_id)

        # Fetch all existing FamilyInformation for the member
        existing_family_info = FamilyInformation.objects.filter(member=member)

        # Handle existing family members
        forms = []
        i = 0
        while f'family-{i}-family_member_name' in self.request.POST:
            instance = existing_family_info.order_by('id')[i] if i < existing_family_info.count() else None
            form = FamilyInformationForm(self.request.POST, instance=instance, prefix=f'family-{i}')
            forms.append(form)
            if not form.is_valid():
                return self.form_invalid(form)
            i += 1

        # Save forms
        print(self.request.POST)
        print(forms)
        for form in forms:
            family_info = form.save(commit=False)
            family_info.member = member
            family_info.save()

        messages.success(self.request, "Family information updated successfully!")
        # Redirect to the 'update_livestock_info' page after saving the data
        return redirect('update_livestock_info', member_id=member.id)

    def get(self, request, *args, **kwargs):
        """Handle GET requests to render forms."""
        context = self.get_initial()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """Handle POST requests for form submission."""
        return self.form_valid(None)
    

def update_livestock_info_view(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    livestock_info = LivestockInformation.objects.filter(member=member).first()

    if request.method == 'POST':
        form = LivestockInformationForm(request.POST, instance=livestock_info)
        if form.is_valid():
            livestock_info = form.save(commit=False)
            livestock_info.member = member
            livestock_info.save()
            messages.success(request, "Live stock information updated successfully!")
            return redirect('update_house_info', member_id=member.id)
    else:
        form = LivestockInformationForm(instance=livestock_info)

    return render(request, 'member/add_member/livestock_info.html', {'form': form, 'member': member})

def update_house_info_view(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    house_info = HouseInformation.objects.filter(member=member).first()

    if request.method == 'POST':
        form = HouseInformationForm(request.POST, instance=house_info)
        if form.is_valid():
            house_info = form.save(commit=False)
            house_info.member = member
            house_info.save()
            messages.success(request, "House information updated successfully!")
            return redirect('update_land_info', member_id=member.id)
    else:
        form = HouseInformationForm(instance=house_info)

    return render(request, 'member/add_member/house_info.html', {'form': form, 'member': member})

def update_land_info_view(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    land_info = LandInformation.objects.filter(member=member).first()

    if request.method == 'POST':
        form = LandInformationForm(request.POST, instance=land_info)
        if form.is_valid():
            land_info = form.save(commit=False)
            land_info.member = member
            land_info.save()
            messages.success(request, "Land information updated successfully!")
            return redirect('update_income_info', member_id=member.id)
    else:
        form = LandInformationForm(instance=land_info)

    return render(request, 'member/add_member/land_info.html', {'form': form, 'member': member})

def update_income_info(request, member_id):
    # Fetch the member and their existing IncomeInformation if it exists
    member = get_object_or_404(Member, id=member_id)
    income_info = IncomeInformation.objects.filter(member=member).first()

    if request.method == 'POST':
        # Bind the form with the existing instance if available, otherwise create a new one
        form = IncomeInformationForm(request.POST, instance=income_info)
        if form.is_valid():
            # Save the form and associate it with the member
            income_info = form.save(commit=False)
            income_info.member = member
            income_info.save()
            messages.success(request, "Income information updated successfully!")
            return redirect('update_expenses_info', member_id=member.id)
    else:
        # Initialize the form with the existing data if available
        form = IncomeInformationForm(instance=income_info)

    return render(request, 'member/add_member/income_info.html', {'form': form, 'member': member})

# Step 4: Expenses Information Update
def update_expenses_info(request, member_id):
    # Fetch the member and their existing ExpensesInformation if it exists
    member = get_object_or_404(Member, id=member_id)
    expenses_info = ExpensesInformation.objects.filter(member=member).first()

    if request.method == 'POST':
        # Bind the form with the existing instance if available, otherwise create a new one
        form = ExpensesInformationForm(request.POST, instance=expenses_info)
        if form.is_valid():
            # Save the form and associate it with the member
            expenses_info = form.save(commit=False)
            expenses_info.member = member
            expenses_info.save()
            messages.success(request, "Expenses information updated successfully!")
            try:
                if request.session['demanding_loan']:
                    return redirect('loan_demand_form', member_id=member.id)
            except:
                return redirect('member_detail', member_id=member.id)
    else:
        # Initialize the form with the existing data if available
        form = ExpensesInformationForm(instance=expenses_info)

    return render(request, 'member/add_member/expenses_info.html', {'form': form, 'member': member})

# Final Step: Save all information atomically

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
    

def member_detail_view(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    personal_info = member.personalInfo
    address_info = member.address_info.filter(address_type='current').first()
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
           queryset = Member.objects.all().select_related('personalInfo').prefetch_related(current_address_prefetch).filter(status__iexact=status_filter)
        return queryset
    

def change_member_status(request):
    if request.method == 'POST':
        # Debug: Log the POST data
        print("POST data:", request.POST)
        member_id = request.POST.get('memberId')
        new_status = request.POST.get('status')

        # Fetch member and validate
        member = get_object_or_404(Member, id=member_id)
       
        # Handle account creation and fees
        if request.POST.get('create_accounts') == 'yes':
            try:
                with transaction.atomic():
                    # Constants for fees
                    MEMBERSHIP_FEE = 100.00
                    PASSBOOK_FEE = 25.00
                    TOTAL_FEE = MEMBERSHIP_FEE + PASSBOOK_FEE

                    # Ensure current teller exists
                    current_teller = Teller.objects.filter(employee=request.user).first()
                    print(current_teller)
                    if not current_teller:
                        return JsonResponse({'success': False, 'error': 'Current Teller not found'}, status=400)

                    # Loop through account types and create accounts
                    for account_code, account_name in INITIAL_SAVING_ACCOUNT_TYPE:
                        amount = 200.0 if account_code == "CS" else 10.0 if account_code == "CF" else 0
                        
                        # Create savings account
                        SavingsAccount.objects.create(
                            member=member,
                            account_type=account_code,
                            account_number=f"{member.code}.{account_code}.1",
                            amount=amount,
                            balance=0.00,
                        )

                        # Adjust teller balance and create voucher for "CS" account type
                        if account_code == "CS":
                            current_teller.balance += Decimal(TOTAL_FEE)
                            current_teller.save()

                            voucher = Voucher.objects.create(
                                voucher_type='Receipt',
                                category='Service Fee',
                                amount=TOTAL_FEE,
                                narration=f"Membership and Passbook Fee for {member.code}",
                                transaction_date=timezone.now(),
                                created_by=request.user,
                            )
                            print(voucher)
                    member.status = new_status
                    member.registered_date = timezone.now().date()
                    member.save()
            except Exception as e:
                print("Error:", str(e))
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
        elif request.POST.get('create_accounts') == 'no':
            member.status = new_status
            member.save()
            messages.success(request, f"Member status updated to {new_status} for {member.personalInfo.first_name}  {member.personalInfo.middle_name}  {member.personalInfo.last_name}.")
            return JsonResponse({'success': True})

        # Redirect to the member list with status 'A' (Active)
        if new_status == 'A':
            messages.success(request, f"Member status updated to Active and accounts created successfully for {member.name}.")
            return HttpResponseRedirect(f"{reverse('member_list')}?status=A")

        messages.success(request, f"Member status updated to {new_status} for {member.name}.")
        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)


def deposits(request):
    return render(request, 'dashboard/deposits.html')

def transactions(request):
    return render(request, 'dashboard/transactions.html')

def reports(request):
    return render(request, 'dashboard/reports.html')