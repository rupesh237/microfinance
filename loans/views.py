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
from core.models import  Voucher, Teller 

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
        user = self.request.user
        if user.is_superuser:
            loans = Loan.objects.prefetch_related('emi_payments')
        else:
            loans = Loan.objects.filter(member__center__branch=user.employee_detail.branch).prefetch_related('emi_payments')
        
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
    # Initialize total amounts
    total_principal_amount = 0
    total_interest_amount = 0
    for schedule in emi_schedules.values():
        for emi in schedule:
            total_principal_amount += emi['principal_component']
            total_interest_amount += emi['interest_component']
            
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

            current_teller = Teller.objects.filter(employee=request.user).first()
            if current_teller is None:
                messages.error(request, "No teller detected for given employee.")
                return redirect('member_loans', member_id=member.id)

            # Create voucher for payment
            voucher = Voucher.objects.create(
                voucher_type='Receipt',
                category='Loan',
                amount=payment.amount_paid,
                narration=f'Loan Receipt of {loan.member.personalInfo.first_name} {loan.member.personalInfo.middle_name} {loan.member.personalInfo.last_name}: {payment.amount_paid}',
                transaction_date=timezone.now().date(),
                created_by=request.user,
                branch=request.user.employee_detail.branch,
            )

            payment.voucher = voucher
            payment.save()

            # Update teller balance
            current_teller.balance += payment.amount_paid
            current_teller.save()

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
        'total_principal_amount': total_principal_amount,
        'total_interest_amount': total_interest_amount,
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
    request.session['demanding_loan'] = True
    print(request.session['demanding_loan'])
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




## LOAN DEMAND ##
def loan_demand_form(request, member_id):
    member = get_object_or_404(Member, id =member_id)
    if 'demanding_loan' in request.session:
        del request.session['demanding_loan']
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
    installment_amount = loan.installement_amount

    # Initialize total amounts
    total_principal_amount = 0
    total_interest_amount = 0

    for emi in emi_schedules:
        total_principal_amount += emi['principal_component']
        total_interest_amount += emi['interest_component']

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
                   'emi_schedules':emi_schedules,
                   'total_principal_amount': total_principal_amount,
                   'total_interest_amount': total_interest_amount,
                   })

def loan_payment(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    emi_schedules = loan.calculate_emi_breakdown()
    installment_amount = loan.installement_amount

     # Initialize total amounts
    total_principal_amount = 0
    total_interest_amount = 0

    for emi in emi_schedules:
        total_principal_amount += emi['principal_component']
        total_interest_amount += emi['interest_component']


    if request.method == "POST":
        if not request.POST.get('cash_payment'):
            messages.error(request, "Payment method is required.")
            return redirect('loan_payment', loan_id=loan.id)
        
        if loan.status == "active":
            messages.warning(request, "This loan is already active.")
            return redirect('loan_disburse_list', member_id=loan.member.id)
        
        if request.POST.get('cash_payment') == 'yes':
            current_teller = Teller.objects.filter(employee=request.user).first()
            if current_teller.balance < loan.loan_analysis_amount:
                messages.error(request, "Sorry, insufficeint balance.")
                return redirect('loan_disburse_list', member_id=loan.member.id)
            else:
                current_teller.balance -= loan.loan_analysis_amount
                current_teller.save()

                # Create voucher for payment
                Voucher.objects.create(
                    voucher_type='Payment',
                    category='Loan',
                    amount=loan.loan_analysis_amount,
                    narration=f'Loan Payment of {loan.member.personalInfo.first_name} {loan.member.personalInfo.middle_name} {loan.member.personalInfo.last_name}: {loan.amount}',
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
        'total_principal_amount': total_principal_amount,
        'total_interest_amount': total_interest_amount,
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

