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

            # Create voucher for payment
            voucher = Voucher.objects.create(
                voucher_type='Receipt',
                category='Loan',
                amount=payment.amount_paid,
                description=f'Loan Receipt of {loan.member.personalInfo.first_name} {loan.member.personalInfo.middle_name} {loan.member.personalInfo.last_name}: {payment.amount_paid}',
                transaction_date=timezone.now().date(),
                created_by=request.user,
            )

            payment.voucher = voucher
            payment.save()

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
    personal_info = get_object_or_404(PersonalInformation, id=member_id)
    gender = personal_info.gender
    marital_status = personal_info.marital_status
    print(f'Gender: {gender}')
    print(f'Marital Status: {marital_status}')
    if gender == 'Male' or (gender == 'Female' and marital_status == 'Single'):
        predefined_relationships = ['Grandfather', 'Father', 'Mother']
    else:
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
            'form': form,
            'member':member
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


from decimal import Decimal, InvalidOperation
from django.utils import timezone

# Need to be updated
@login_required
def confirm_clear_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)

    # Ensure loan is not already cleared
    if loan.is_cleared:
        messages.info(request, f'Loan "{loan.loan_type}" is already cleared.')
        return HttpResponseRedirect(reverse('member_loans', args=[loan.member.id]))

    # Calculate remaining principal
    total_principal_paid = sum(payment.principal_paid for payment in loan.emi_payments.all())
    remaining_principal = loan.amount - total_principal_paid

    # Calculate accrued interest
    last_payment = EMIPayment.get_last_payment(loan)
    last_payment_date = last_payment.payment_date if last_payment else loan.loan_disburse_date
    today = timezone.now().date()
    days_since_last_payment = max((today - last_payment_date).days, 0)
    daily_interest_rate = loan.interest_rate / 365 / 100
    accrued_interest = round(remaining_principal * daily_interest_rate * days_since_last_payment, 2)
    total_due = remaining_principal + accrued_interest

    if request.method == 'GET':
        return render(request, 'loans/confirm_clear_loan.html', {
            'loan': loan,
            'remaining_principal': remaining_principal,
            'accrued_interest': accrued_interest,
            'total_due': total_due,
            'days_since_last_payment': days_since_last_payment,
        })

    if request.method == 'POST':
        try:
            amount_paid = Decimal(request.POST.get('amount_paid'))
            if amount_paid == total_due:
                EMIPayment.objects.create(
                    loan=loan,
                    payment_date=today,
                    amount_paid=amount_paid,
                    principal_paid=remaining_principal,
                    interest_paid=accrued_interest,
                )
                loan.is_cleared = True
                loan.status = 'closed'
                loan.save()
                messages.success(request, f'Loan "{loan.loan_type}" has been successfully cleared.')
                return HttpResponseRedirect(reverse('member_loans', args=[loan.member.id]))
            else:
                messages.error(request, 'The amount entered does not match the outstanding total due.')
        except (ValueError, InvalidOperation):
            messages.error(request, 'Invalid payment amount entered.')

    return HttpResponseRedirect(reverse('confirm_clear_loan', args=[loan.id]))


@login_required
def cleared_loans(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    loans = member.loans.filter(is_cleared=True).prefetch_related('emi_payments')
    return render(request, 'loans/cleared_loans.html', {
        'member': member,
        'loans': loans,
        'payment_history': {loan.id: loan.emi_payments.all() for loan in loans},
    })

