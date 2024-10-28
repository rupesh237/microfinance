from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

from django.views.generic import (
    CreateView, ListView, UpdateView, DeleteView )

from .models import Employee, District, Municipality, Branch, GRoup, Member, Center,PersonalInformation, FamilyInformation, LivestockInformation, HouseInformation, LandInformation, IncomeInformation, ExpensesInformation
from savings.models import SavingsAccount, INITIAL_SAVING_ACCOUNT_TYPE

from .forms import BranchForm, EmployeeForm, CenterForm, GroupForm

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
    groups = GRoup.objects.all()
    centers = Center.objects.all()
    employees = Employee.objects.all()
    return render(request, "dashboard/admin_dashboard.html",{
        'bank': 'Admin',
        'groups': groups,
        'centers': centers,
        'employees': employees,
        'members': members
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



from .forms import (
    CenterSelectionForm, AddressInformationForm, PersonalInformationForm, FamilyInformationForm, 
    LivestockInformationForm, HouseInformationForm, LandInformationForm, 
    IncomeInformationForm, ExpensesInformationForm
)
from formtools.wizard.views import SessionWizardView
from django.shortcuts import redirect

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
        return [TEMPLATES.get(self.steps.current)]

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

                # Create the Member object now that we have all necessary information
                member = Member.objects.create(
                    center_id=center_id,
                    group_id=group_id,
                    member_code=member_code,
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

        except Exception as e:
            # Handle exception if saving fails
            messages.error(self.request, f"Error saving member: {e}")
            return redirect('member_list')
        member_id = self.request.session.get('member_id')
        if not member_id:
            # Replace this with actual member creation logic if not in session
            member = Member.objects.create()  # Assuming Member creation doesn't need extra params
            self.request.session['member_id'] = member.id
        else:
            member = Member.objects.get(id=member_id)

        # Save main forms
        for form in form_list:
            if form.is_valid():
                instance = form.save(commit=False)
                instance.member = member
                instance.save()
            else:
                print("Form validation error:", form.errors)
                return self.render_goto_step(self.steps.first())  # Go back if any form invalid

        # Save family forms from extra_data
        family_data_list = self.storage.extra_data.pop('family_forms_data', [])
        for family_data in family_data_list:
            family_member_form = FamilyInformationForm(data=family_data)
            if family_member_form.is_valid():
                family_member = family_member_form.save(commit=False)
                family_member.member = member
                family_member.save()
            else:
                print("Family member form validation error:", family_member_form.errors)
                return self.render_goto_step('family')  # Return to family step if any invalid

        # Final redirection after successful save of all forms
        return redirect('member_list')


# def select_group(request):
#     if request.method == 'POST':
#         form = GroupSelectionForm(request.POST)
#         if form.is_valid():
#             request.session['group'] = form.cleaned_data['group'].id
#             return redirect('add_member')
#     else:
#         form = GroupSelectionForm()
#     return render(request, 'dashboard/select_group.html', {'form': form})

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

class SelectCenterView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Member
    form_class = CenterSelectionForm
    template_name = 'dashboard/select_center.html'
    success_url = reverse_lazy('add_member')
    template_name = 'member/add_member/select_center.html'
    success_url = reverse_lazy('add_member') 

    def form_valid(self, form):
        # Store center and group information in the session instead of saving the Member
        center_id = form.cleaned_data['center'].id
        group_id = form.cleaned_data['group'].id
        member_code = form.cleaned_data['member_code']
        
        # Store these details in the session
        self.request.session['center_id'] = center_id
        self.request.session['group_id'] = group_id
        self.request.session['member_code'] = member_code

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

   
class MemberDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Member
    success_url = reverse_lazy('member_list')
    template_name = 'member/delete_member.html'


def member_detail_view(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    personal_info = member.personalInfo
    family_info = member.familyInfo
    livestock_info = member.livestockInfo
    house_info = member.houseInfo
    land_info = member.landInfo
    income_info = member.incomeInfo
    expenses_info = member.expensesInfo
    
    context = {
        'member': member,
        'personal_info': personal_info,
        'family_info': family_info,
        'livestock_info': livestock_info,
        'house_info': house_info,
        'land_info': land_info,
        'income_info': income_info,
        'expenses_info': expenses_info,
    }
    
    return render(request, 'member/member_detail.html', context)

class MemberListView(ListView):
    model = Member
    template_name = 'member/member_list.html'
    context_object_name = 'members'

    # Pass the MEMBER_STATUS choices to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['member_status'] = Member.MEMBER_STATUS  # Assuming MEMBER_STATUS is defined in the Member model
        return context


    def get_queryset(self):
        queryset = Member.objects.all().select_related('personalInfo').filter(status='A')
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
                    account_type=account_name,
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