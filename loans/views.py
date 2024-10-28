# loans/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Loan, EMIPayment
from .forms import LoanForm, EMIPaymentForm  # Create EMIPaymentForm as needed
from dashboard.models import Member, PersonalInformation, FamilyInformation, LivestockInformation, HouseInformation, LandInformation, IncomeInformation, ExpensesInformation
from dashboard.forms import PersonalInformationForm, FamilyInformationForm, LivestockInformationForm, HouseInformationForm, LandInformationForm, IncomeInformationForm, ExpensesInformationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.mixins import RoleRequiredMixin
from django.contrib import messages
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

from formtools.wizard.views import SessionWizardView

@login_required
def member_loans(request, member_id):
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
        form = LoanForm(initial={'member': member})
        payment_form = EMIPaymentForm()

    loan_id = request.GET.get('loan_id')
    if loan_id:
        loan = get_object_or_404(Loan, id=loan_id)
        emi_schedule = loan.calculate_emi_breakdown()

    payment_history = {loan.id: loan.emi_payments.all() for loan in loans}

    return render(request, 'loans/member_loans.html', {
        'member': member,
        'loans': loans,
        'form': form,
        'emi_schedule': emi_schedule,
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
        form = LoanForm(initial={'member': member})
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

class UpdateMemberInfoforLoan(LoginRequiredMixin, RoleRequiredMixin, SessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_form_initial(self, step):
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
                            'earning': form_instance.earning,
                            'farming_income': form_instance.farming_income,
                            'cattle_income': form_instance.cattle_income,
                        }
                    )
                elif isinstance(form_instance, ExpensesInformation):
                    ExpensesInformation.objects.update_or_create(
                        member=member,
                        defaults={
                            'house_rent': form_instance.house_rent,
                            'food_expense': form_instance.food_expense,
                            'health_expense': form_instance.health_expense,
                            'other_expenses': form_instance.other_expenses,
                        }
                    )

        return redirect('loan_form', member_id=member.id)

    

def take_loan(request, member_id):
    member = get_object_or_404(Member, id =member_id)
    loans = member.loans.all()
    return render (request, 'loans/take_loan.html', {
        'member': member,
        'loans': loans
    })

def loan_form(request, member_id):
    member = get_object_or_404(Member, id =member_id)
    form = LoanForm()
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.member = member
            loan.save()
            return redirect('member_loans', member_id=member.id)
    else:
        form = LoanForm(initial={'member': member})
        return render (request, 'loans/loan_form.html',{
            'form': form
        })
    return render (request, 'loans/loan_form.html', {
        'form': form,
        'member':member
    })
