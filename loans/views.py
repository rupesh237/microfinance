# loans/views.py
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.mixins import RoleRequiredMixin
from django.contrib import messages
from django.template.loader import get_template
from django.views.generic import ListView

from .models import Loan, EMIPayment
from .forms import LoanDemandForm, LoanAnalysisForm, LoanDisburseForm, EMIPaymentForm  # Create EMIPaymentForm as needed
from dashboard.models import Member, PersonalInformation, AddressInformation, FamilyInformation, LivestockInformation, HouseInformation, LandInformation, IncomeInformation, ExpensesInformation
from dashboard.forms import PersonalInformationForm, AddressInformationForm, FamilyInformationForm, LivestockInformationForm, HouseInformationForm, LandInformationForm, IncomeInformationForm, ExpensesInformationForm
from core.models import  Voucher

from xhtml2pdf import pisa
from django.utils import timezone
from django.db import transaction
from django.views.generic import UpdateView
import nepali_datetime
from django.db.models import Subquery, OuterRef


from formtools.wizard.views import SessionWizardView

class LoanListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Loan
    template_name = 'loans/loan_list.html'
    context_object_name = 'loans'

    def get_queryset(self):
        loans = Loan.objects.prefetch_related('emi_payments')
        
        # Annotate loans with the latest payment
        for loan in loans:
            latest_payment = loan.emi_payments.order_by('-payment_date').first()
            if latest_payment:
                loan.last_amount_paid = latest_payment.amount_paid
                loan.last_closing_balance = latest_payment.closing_balance
            else:
                loan.last_amount_paid = 0.00
                loan.last_closing_balance = loan.amount

        return loans


@login_required
def member_loans(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    # Fetch only non-cleared loans
    loans = member.loans.filter(status='active', is_cleared=False)
    emi_schedules = {loan.id: loan.calculate_emi_breakdown() for loan in loans}
    payment_form = None

    if request.method == 'POST':
        payment_form = EMIPaymentForm(request.POST)
        if payment_form.is_valid():
            payment = payment_form.save(commit=False)
            loan = payment.loan
            emi_schedule = loan.calculate_emi_breakdown()
            current_month = len(loan.emi_payments.all()) + 1
            emi_info = emi_schedule[current_month - 1]

            payment.principal_paid = emi_info['principal_component']
            payment.interest_paid = emi_info['interest_component']
            payment.save()

            # Create voucher for payment
            Voucher.objects.create(
                voucher_type='Receipt',
                category='Loan',
                amount=loan.loan_analysis_amount,
                description=f'Loan Receipt of {loan.member.personalInfo.first_name} {loan.member.personalInfo.middle_name} {loan.member.personalInfo.last_name}: {loan.amount}',
                transaction_date=timezone.now().date(),
                created_by=request.user,
            )

            # Mark loan as cleared if balance is zero after this payment
            if payment.closing_balance == 0:
                loan.is_cleared = True
                loan.save()

            messages.success(request, f"EMI payment has been received successfully!")
            return redirect('member_loans', member_id=member.id)

    else:
        form = LoanDemandForm(initial={'member': member})
        payment_form = EMIPaymentForm()

    payment_history = {loan.id: loan.emi_payments.all() for loan in loans}

    return render(request, 'loans/member_loans.html', {
        'member': member,
        'loans': loans,
        'form': form,
        'emi_schedules': emi_schedules,
        'payment_form': payment_form,
        'payment_history': payment_history,
    })

def pdf_report(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    loans = member.loans.all()
    emi_schedule = []
    payment_form = None

    if request.method == 'POST':
        payment_form = EMIPaymentForm(request.POST)
        if payment_form.is_valid():
            payment = payment_form.save(commit=False)
            loan = payment.loan

            # Calculate EMI schedule and fetch the corresponding EMI info for the current month
            emi_schedule = loan.calculate_emi_breakdown()
            current_month = len(loan.emi_payments.all()) + 1  # Increment for the next payment month
            emi_info = emi_schedule[current_month - 1]

            payment.principal_paid = emi_info['principal_component']
            payment.interest_paid = emi_info['interest_component']
            payment.save()

            return redirect('member_loans', member_id=member.id)

    else:
        form = LoanDemandForm(initial={'member': member})
        payment_form = EMIPaymentForm()

    loan_id = request.GET.get('loan_id')
    if loan_id:
        loan = get_object_or_404(Loan, id=loan_id)
        emi_schedule = loan.calculate_emi_breakdown()

    payment_history = {loan.id: loan.emi_payments.all() for loan in loans}
    template_path = 'loans/pdf_report.html'
    context ={
        'member': member,
        'loans': loans,
        'form': form,
        'emi_schedule': emi_schedule,
        'payment_form': payment_form,
        'payment_history': payment_history,
    }
    response = HttpResponse(content_type = 'application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# Member information change views for loan applications
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
            return redirect("update_personal_info_for_loan", member_id=member.id)

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
        member_id = self.object.member_id
        personal_info.save()

        # Redirect to the member detail view with the correct URL argument
        return redirect(reverse('update_family_info_for_loan', kwargs={'member_id': member_id}))

    def form_invalid(self, form):
        """Handle invalid forms."""
        return self.render_to_response(self.get_context_data(form=form))

def update_family_info_view(request, member_id):
    member = get_object_or_404(Member, id=member_id)

    # Define relationships that should not be modified
    predefined_relationships = ['Father', 'Husband', 'Father-In-Law']
    
    # Fetch all existing FamilyInformation for the member
    existing_family_info = FamilyInformation.objects.filter(member=member)

    # Split forms into predefined and dynamic based on relationship
    predefined_forms = []
    dynamic_forms = []

    if request.method == 'POST':
        valid = True

        # Handle predefined relationships
        for relationship in predefined_relationships:
            instance = existing_family_info.filter(relationship=relationship).first()
            form = FamilyInformationForm(
                request.POST,
                instance=instance,
                prefix=f'predefined-{relationship}'
            )
            predefined_forms.append(form)
            if not form.is_valid():
                valid = False

        # Handle dynamically added relationships
        i = 0
        while f'dynamic-form-{i}-family_member_name' in request.POST:
            instance = existing_family_info.exclude(relationship__in=predefined_relationships).order_by('id')[i] if i < existing_family_info.exclude(relationship__in=predefined_relationships).count() else None
            form = FamilyInformationForm(
                request.POST,
                instance=instance,
                prefix=f'dynamic-form-{i}'
            )
            dynamic_forms.append(form)
            if not form.is_valid():
                valid = False
            i += 1

        if valid:
            # Save predefined forms
            for form in predefined_forms:
                family_info = form.save(commit=False)
                family_info.member = member
                family_info.save()

            # Save dynamic forms
            for form in dynamic_forms:
                family_info = form.save(commit=False)
                family_info.member = member
                family_info.save()

            return redirect('update_livestock_info_for_loan', member_id=member.id)
    else:
        # Initialize predefined forms
        for relationship in predefined_relationships:
            instance = existing_family_info.filter(relationship=relationship).first()
            form = FamilyInformationForm(
                instance=instance,
                initial={'relationship': relationship},
                prefix=f'predefined-{relationship}'
            )
            predefined_forms.append(form)

        # Initialize dynamic forms
        dynamic_family_info = existing_family_info.exclude(relationship__in=predefined_relationships)
        for i, instance in enumerate(dynamic_family_info):
            form = FamilyInformationForm(instance=instance, prefix=f'dynamic-form-{i}')
            dynamic_forms.append(form)

    return render(request, 'member/update_family_info.html', {
        'member': member,
        'predefined_forms': predefined_forms,
        'dynamic_forms': dynamic_forms,
    })

def update_livestock_info_view(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    livestock_info = LivestockInformation.objects.filter(member=member).first()

    if request.method == 'POST':
        form = LivestockInformationForm(request.POST, instance=livestock_info)
        if form.is_valid():
            livestock_info = form.save(commit=False)
            livestock_info.member = member
            livestock_info.save()
            return redirect('update_house_info_for_loan', member_id=member.id)
    else:
        form = LivestockInformationForm(instance=livestock_info)

    return render(request, 'member/update_livestock_info.html', {'form': form, 'member': member})

def update_house_info_view(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    house_info = HouseInformation.objects.filter(member=member).first()

    if request.method == 'POST':
        form = HouseInformationForm(request.POST, instance=house_info)
        if form.is_valid():
            house_info = form.save(commit=False)
            house_info.member = member
            house_info.save()
            return redirect('update_land_info_for_loan', member_id=member.id)
    else:
        form = HouseInformationForm(instance=house_info)

    return render(request, 'member/update_house_info.html', {'form': form, 'member': member})

def update_land_info_view(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    land_info = LandInformation.objects.filter(member=member).first()

    if request.method == 'POST':
        form = LandInformationForm(request.POST, instance=land_info)
        if form.is_valid():
            land_info = form.save(commit=False)
            land_info.member = member
            land_info.save()
            return redirect('update_income_info_for_loan', member_id=member.id)
    else:
        form = LandInformationForm(instance=land_info)

    return render(request, 'member/update_land_info.html', {'form': form, 'member': member})

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
            return redirect('update_expenses_info_for_loan', member_id=member.id)
    else:
        # Initialize the form with the existing data if available
        form = IncomeInformationForm(instance=income_info)

    return render(request, 'member/update_income_info.html', {'form': form, 'member': member})

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
            return redirect('loan_demand_form', member_id=member.id)
    else:
        # Initialize the form with the existing data if available
        form = ExpensesInformationForm(instance=expenses_info)

    return render(request, 'member/update_expenses_info.html', {'form': form, 'member': member})

# Update member information for loan application ends here.


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

class UpdateMemberInfoforLoan(LoginRequiredMixin, RoleRequiredMixin, SessionWizardView):
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
                    
        return redirect('loan_demand_form', member_id=member.id)

def take_loan(request, member_id):
    member = get_object_or_404(Member, id =member_id)
    loans = member.loans.all()
    return render (request, 'loans/take_loan.html', {
        'member': member,
        'loans': loans
    })

## LOAN DEMAND ##
def loan_demand_form(request, member_id):
    member = get_object_or_404(Member, id =member_id)
    form = LoanDemandForm()
    if request.method == 'POST':
        form = LoanDemandForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.member = member
            loan.save()
            return redirect('loan_demand_list', member_id=member.id)
    else:
        form = LoanDemandForm(initial={'member': member})
        return render (request, 'loans/forms/loan_demand_form.html',{
            'form': form
        })
    return render (request, 'loans/forms/loan_demand_form.html', {
        'form': form,
        'member':member
    })

def loan_demand_list(request, member_id):
    member = get_object_or_404(Member, id =member_id)
    loan = Loan.objects.filter(member=member).first()
    return render (request, 'loans/views/loan_demand_list.html', {
       'loan': loan,
       'member': member
    })

## LOAN ANALYSIS ##
def loan_analysis_list(request, member_id):
    member = get_object_or_404(Member, id =member_id)
    loan = Loan.objects.filter(member=member).first()
    if loan is not None:
        if loan.status == 'analysis' or loan.status != 'applied':
            loan = loan
        else:
            loan = None
    return render (request, 'loans/views/loan_analysis_list.html', {
       'loan': loan,
       'member': member
    })

def loan_analysis_form(request,loan_id):
    loan_instance = get_object_or_404(Loan, id=loan_id) 
    member = get_object_or_404(Member, pk=loan_instance.member.id)

    # Fetch the existing IncomeInformation for the member or create one if none exists
    income_info = IncomeInformation.objects.get(member=member)
    expenses_info = ExpensesInformation.objects.get(member=member)

    if request.method == 'POST':
        income_form = IncomeInformationForm(request.POST, instance=income_info, prefix='income')
        expenses_form = ExpensesInformationForm(request.POST,  instance=expenses_info, prefix='expenses')
        loan_analysis_form = LoanAnalysisForm(request.POST, instance=loan_instance, prefix='loan_analysis')
        
        if income_form.is_valid() and expenses_form.is_valid():
            income_form.save()  # Save updates to the existing instance
            expenses_form.save()

            loan_info = loan_analysis_form.save(commit=False)
            loan_info.status = "analysis"
            loan_info.save() 
            return redirect('loan_demand_list', member_id=member.id)
    else:
        income_form = IncomeInformationForm(instance=income_info, prefix='income')
        expenses_form = ExpensesInformationForm(instance=expenses_info, prefix='expenses')
        loan_analysis_form = LoanAnalysisForm(prefix='loan_analysis', loan_instance=loan_instance)

    context = {
        'income_form': income_form,
        'expenses_form': expenses_form,
        'loan_analysis_form': loan_analysis_form,
    }
    return render(request, 'loans/forms/loan_analysis_form.html', context)

## LOAN DISBURSE ##
def loan_disburse_list(request, member_id):
    """
    This view renders the list of loans which are ready for disbursement.
    """
    member = get_object_or_404(Member, id =member_id)
    # Fetch the latest loan of the member which is ready for disbursement
    loan = Loan.objects.filter(member=member).first()
    if loan is not None:
        # If the loan is in disburse or active status, show it to the user
        if loan.status == 'disburse' or loan.status == 'approved' or loan.status == 'active':
            loan = loan
        else:
            # If the loan is in any other status, don't show it to the user
            loan = None
    return render (request, 'loans/views/loan_disburse_list.html', {
       'loan': loan,
       'member': member
    })

@csrf_exempt
def preview_schedule(request):
    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get("amount", "0"))
            interest_rate = Decimal(request.POST.get("interest_rate", "0"))
            duration_months = int(request.POST.get("duration_months", "0"))
            loan_type = request.POST.get("loan_type", "flat")

            # Simulate Loan object for EMI calculation
            loan = Loan(
                amount=amount,
                interest_rate=interest_rate,
                duration_months=duration_months,
                loan_type=loan_type
            )
            schedule = loan.calculate_emi_breakdown()

            return JsonResponse({
                "success": True,
                "schedule": [
                    {
                        "month": row["month"],
                        "emi_amount": float(row["emi_amount"]),  # Ensure it's a float
                        "principal_component": float(row["principal_component"]),
                        "interest_component": float(row["interest_component"]),
                        "remaining_principal": float(row["remaining_principal"]),
                    } for row in schedule
                ],
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request"})


def loan_disburse_form(request, loan_id):
    loan_instance = get_object_or_404(Loan, id=loan_id) 
    member = get_object_or_404(Member, pk=loan_instance.member.id)

    if request.method == 'POST':
        form = LoanDisburseForm(request.POST, instance=loan_instance)
        
        if form.is_valid():
            loan_info = form.save(commit=False)
            emis = loan_info.calculate_emi_breakdown()[0]
            loan_info.installement_amount = emis['emi_amount']
            loan_info.status = "disburse"
            loan_info.save() 
            return redirect('loan_analysis_list', member_id=member.id)
        
    else:
        form = LoanDisburseForm(loan_instance=loan_instance)

    context = {
        'form': form,
    }
    return render(request, 'loans/forms/loan_disburse_form.html', context)


## LOAN PAYMNET ##
def loan_payment_list(request, member_id):
    member = get_object_or_404(Member, id =member_id)
    loan = Loan.objects.filter(member=member).first()
    if loan is not None:
        if loan.status == 'active':
            loan = loan
        else:
            loan = None
    return render (request, 'loans/views/loan_payment_list.html', {
       'loan': loan,
       'member': member
    })

def approve_loan(request, loan_id):
    # Approve the loan (your logic here)
    loan = Loan.objects.get(id=loan_id)
    emi_schedules = loan.calculate_emi_breakdown()
    installment_amount = emi_schedules[0]['emi_amount']

    if request.method == "POST":
        loan = get_object_or_404(Loan, id=loan_id)
        # Update the loan status
        loan.status = "approved"
        loan.save()
        messages.success(request, f"Loan has been approved successfully!")
        return redirect('loan_disburse_list', member_id=loan.member.id)

    # Pass a flag to the template to show the modal
    return render(request, 'loans/views/loan_approve.html', 
                  {'loan': loan,
                   'installment_amount': installment_amount,
                   'emi_schedules':emi_schedules
                   })

def loan_payment(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    emi_schedules = loan.calculate_emi_breakdown()
    installment_amount = emi_schedules[0]['emi_amount']

    if request.method == "POST":
        if not request.POST.get('cash_payment'):
            messages.error(request, "Payment method is required.")
            return redirect('loan_payment', loan_id=loan.id)
        
        if loan.status == "active":
            messages.warning(request, "This loan is already active.")
            return redirect('loan_disburse_list', member_id=loan.member.id)
        
        if request.POST.get('cash_payment') == 'yes':
            # Create voucher for payment
            Voucher.objects.create(
                voucher_type='Payment',
                category='Loan',
                amount=loan.loan_analysis_amount,
                description=f'Loan Payment of {loan.member.personalInfo.first_name} {loan.member.personalInfo.middle_name} {loan.member.personalInfo.last_name}: {loan.amount}',
                transaction_date=timezone.now().date(),
                created_by=request.user,
            )
            # Update the loan status
            loan.status = "active"
            loan.created_by = request.user
            loan.created_date = timezone.now().date()
            loan.save()  
            messages.success(request, "Loan payment made successfully!")
            return redirect('loan_disburse_list', member_id=loan.member.id)

    # Render payment form
    context = {
        'loan': loan,
        'installment_amount': installment_amount,
        'emi_schedules': emi_schedules,
    }
    return render(request, 'loans/forms/loan_payment.html', context)


from decimal import Decimal
from django.utils import timezone

@login_required
def confirm_clear_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)

    # Calculate the total principal paid so far
    total_principal_paid = sum(payment.principal_paid for payment in loan.emi_payments.all())
    remaining_principal = loan.amount - total_principal_paid

    # Check if the loan is already cleared
    if loan.is_cleared:
        messages.info(request, f'Loan "{loan.loan_type}" is already cleared.')
        return HttpResponseRedirect(reverse('member_loans', args=[loan.member.id]))

    # Get the last payment date or use the start date of the loan
    last_payment = EMIPayment.get_last_payment(loan)
    last_payment_date = last_payment.payment_date if last_payment else loan.start_date

    # Calculate the number of days between the last payment and today
    today = timezone.now().date()
    days_since_last_payment = (today - last_payment_date).days

    # Calculate the pro-rata interest for the remaining principal over those days
    if days_since_last_payment > 0:
        daily_interest_rate = loan.interest_rate / 365 / 100  # Annual interest divided by 365 days
        accrued_interest = round(remaining_principal * daily_interest_rate * days_since_last_payment, 2)
    else:
        accrued_interest = Decimal(0)

    # Total amount due is the remaining principal plus accrued interest
    total_due = remaining_principal + accrued_interest

    if request.method == 'GET':
        context = {
            'loan': loan,
            'remaining_principal': remaining_principal,
            'accrued_interest': accrued_interest,
            'total_due': total_due,
            'days_since_last_payment': days_since_last_payment,
        }
        return render(request, 'loans/confirm_clear_loan.html', context)

    # Process the payment when the form is submitted
    if request.method == 'POST':
        amount_paid = Decimal(request.POST.get('amount_paid'))

        if amount_paid == total_due:
            # Create a final payment record to clear the loan
            EMIPayment.objects.create(
                loan=loan,
                payment_date=today,
                amount_paid=amount_paid,
                principal_paid=remaining_principal,
                interest_paid=accrued_interest,
            )

            # Mark the loan as cleared
            loan.is_cleared = True
            loan.status = 'closed'
            loan.save()

            messages.success(request, f'Loan "{loan.loan_type}" has been successfully cleared.')
            return HttpResponseRedirect(reverse('member_loans', args=[loan.member.id]))
        else:
            messages.error(request, 'The amount entered does not match the outstanding total due.')

    return HttpResponseRedirect(reverse('confirm_clear_loan', args=[loan.id]))

@login_required
def cleared_loans(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    # Fetch only cleared loans
    loans = member.loans.filter(is_cleared=True)
    payment_history = {loan.id: loan.emi_payments.all() for loan in loans}
    
    return render(request, 'loans/cleared_loans.html', {
        'member': member,
        'loans': loans,
        'payment_history': payment_history,
    })
