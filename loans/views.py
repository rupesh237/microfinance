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
