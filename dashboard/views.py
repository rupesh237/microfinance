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

from .forms import BranchForm, EmployeeForm, CenterForm, GroupForm

from .mixins import RoleRequiredMixin

from django.utils import timezone


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
        form.instance.created_by = self.request.user
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
    CenterSelectionForm, PersonalInformationForm, FamilyInformationForm, 
    LivestockInformationForm, HouseInformationForm, LandInformationForm, 
    IncomeInformationForm, ExpensesInformationForm
)
from formtools.wizard.views import SessionWizardView

FORMS = [
    ("personal", PersonalInformationForm),
    ("family", FamilyInformationForm),
    ("livestock", LivestockInformationForm),
    ("house", HouseInformationForm),
    ("land", LandInformationForm),
    ("income", IncomeInformationForm),
    ("expenses", ExpensesInformationForm),
]

TEMPLATES = {
    "personal": "member/add_member/personal_info.html",
    "family": "member/add_member/family_info.html",
    "livestock": "member/add_member/livestock_info.html",
    "house": "member/add_member/house_info.html",
    "land": "member/add_member/land_info.html",
    "income": "member/add_member/income_info.html",
    "expenses": "member/add_member/expenses_info.html",
}

class MemberWizard(SessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        # Get the member from the session
        member_id = self.request.session.get('member_id')
        if member_id:
            member = Member.objects.get(id=member_id)
        else:
            # Handle the case where member_id is not found
            return redirect('select_center')

        for form in form_list:
            form_instance = form.save(commit=False)
            form_instance.member = member
            form_instance.save()

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

    def form_valid(self, form):
       member = form.save()  # This creates the Member object

       # Store the member ID in session to access it later in MemberWizard
       self.request.session['member_id'] = member.id
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
    

from django.db import transaction
FORMSS = [
    ("personal", PersonalInformationForm),
    ("family", FamilyInformationForm),
    ("livestock", LivestockInformationForm),
    ("house", HouseInformationForm),
    ("land", LandInformationForm),
    ("income", IncomeInformationForm),
    ("expenses", ExpensesInformationForm),
]

TEMPLATES = {
    "personal": "member/update_member/personal_info.html",
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
        """Return the template name for the current step."""
        return [TEMPLATES[self.steps.current]]

    def get_form_initial(self, step):
        """
        Pre-populate the forms with existing member data for each step.
        """
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(Member, pk=member_id)
        # Fetch related models for the member
        personal_info = get_object_or_404(PersonalInformation, member=member)
        family_info = get_object_or_404(FamilyInformation, member=member)
        livestock_info = get_object_or_404(LivestockInformation, member=member)
        house_info = get_object_or_404(HouseInformation, member=member)
        land_info = get_object_or_404(LandInformation, member=member)
        income_info = get_object_or_404(IncomeInformation, member=member)
        expenses_info = get_object_or_404(ExpensesInformation, member=member)

        # Populate initial data for each step based on the form
        initial = super().get_form_initial(step)

        if step == "personal":
            initial.update({
                'name': personal_info.name,
                'phone_number': personal_info.phone_number,
                'current_address': personal_info.current_address,
                'permanent_address': personal_info.permanent_address,
            })
        elif step == "family":
            initial.update({
                'sons': family_info.sons,
                'daughters': family_info.daughters,
                'husband': family_info.husband,
                'father': family_info.father,
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
                'earning': income_info.earning,
                'farming_income': income_info.farming_income,
                'cattle_income': income_info.cattle_income,
            })
        elif step == "expenses":
            initial.update({
                'house_rent': expenses_info.house_rent,
                'food_expense': expenses_info.food_expense,
                'health_expense': expenses_info.health_expense,
                'other_expenses': expenses_info.other_expenses,
            })

        return initial

    def done(self, form_list, **kwargs):
        """
        Save the updated member information after all steps are completed.
        """
        member_id = self.kwargs.get('member_id')  # Ensure 'member_id' is used consistently
        member = get_object_or_404(Member, pk=member_id)

        with transaction.atomic():  # Ensure all forms save or none
            for form in form_list:
                form_instance = form.save(commit=False)
                # Check if the instance already exists for the related member
                if isinstance(form_instance, PersonalInformation):
                    personal_info, created = PersonalInformation.objects.get_or_create(
                        member=member,
                        defaults={'name': form_instance.name, 'phone_number': form_instance.phone_number,
                                  'current_address': form_instance.current_address, 'permanent_address': form_instance.permanent_address}
                    )
                    if not created:
                        # Update the existing instance
                        personal_info.name = form_instance.name
                        personal_info.phone_number = form_instance.phone_number
                        personal_info.current_address = form_instance.current_address
                        personal_info.permanent_address = form_instance.permanent_address
                        personal_info.save()

                elif isinstance(form_instance, FamilyInformation):
                    family_info, created = FamilyInformation.objects.get_or_create(
                        member=member,
                        defaults={'sons': form_instance.sons, 'daughters': form_instance.daughters,
                                  'husband': form_instance.husband, 'father': form_instance.father}
                    )
                    if not created:
                        # Update the existing instance
                        family_info.sons = form_instance.sons
                        family_info.daughters = form_instance.daughters
                        family_info.husband = form_instance.husband
                        family_info.father = form_instance.father
                        family_info.save()

                # Repeat this pattern for other models like LivestockInformation, HouseInformation, etc.
                # Example for LivestockInformation:
                elif isinstance(form_instance, LivestockInformation):
                    livestock_info, created = LivestockInformation.objects.get_or_create(
                        member=member,
                        defaults={'cows': form_instance.cows, 'buffalo': form_instance.buffalo,
                                  'goat': form_instance.goat, 'sheep': form_instance.sheep}
                    )
                    if not created:
                        # Update the existing instance
                        livestock_info.cows = form_instance.cows
                        livestock_info.buffalo = form_instance.buffalo
                        livestock_info.goat = form_instance.goat
                        livestock_info.sheep = form_instance.sheep
                        livestock_info.save()

                # Repeat for other models (HouseInformation, LandInformation, IncomeInformation, ExpensesInformation)

        return redirect('member_list')


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


def member_list_view(request):
    members =Member.objects.all().select_related('personalInfo')
    return render(request, 'member/member_list.html',{
        'members': members
    })

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