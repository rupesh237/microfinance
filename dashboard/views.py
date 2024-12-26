from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from django.db import transaction

from django.views.generic import (
    CreateView, ListView, UpdateView, DeleteView )

from dashboard.models import Employee, District, Municipality, Branch, GRoup, Member, Center,AddressInformation, PersonalInformation, FamilyInformation, LivestockInformation, HouseInformation, LandInformation, IncomeInformation, ExpensesInformation
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

    def get_queryset(self):
        queryset = Center.objects.all()
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

class CenterDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Center
    success_url = reverse_lazy('center_list')
    template_name = 'center/delete_center.html'


## GROUPS ##
class GroupListView(LoginRequiredMixin, ListView):
    model = GRoup
    context_object_name = 'groups'
    template_name = 'group/group_list.html'

    def get_queryset(self):
        queryset = GRoup.objects.all()
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
    address_info = member.addressInfo
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
                # Set default amount based on account_code
                if account_code == "CS":
                    amount = 200.0
                elif account_code == "CF":
                    amount = 10.0
                else:
                    amount = 0 
                SavingsAccount.objects.create(
                    member=member,
                    account_type=account_code,
                    account_number=f"{member.code}.{account_code}.1", 
                    amount=amount,
                    balance=0.00,
                )
            
        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)


@login_required
def branch_list_view(request):
    branches = Branch.objects.all()
    paginator = Paginator(branches, 10)  # Show 10 centers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'branch/branch_list.html', {'branches': page_obj})


@login_required
def employee_list_view(request):
    employees = Employee.objects.all().select_related('user')
    paginator = Paginator(employees, 10)  # Show 10 centers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'employee/employee_list.html', {
        'employees': page_obj
    })



def deposits(request):
    return render(request, 'dashboard/deposits.html')

def transactions(request):
    return render(request, 'dashboard/transactions.html')

def reports(request):
    return render(request, 'dashboard/reports.html')