# loans/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Loan, EMIPayment
from .forms import LoanForm, EMIPaymentForm  # Create EMIPaymentForm as needed
from dashboard.models import Member

@login_required
def member_loans(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    loans = member.loans.all()
    emi_schedule = []
    payment_form = None

    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.member = member
            loan.save()
            return redirect('member_loans', member_id=member.id)

        # Handle EMI payment submission
        payment_form = EMIPaymentForm(request.POST)
        if payment_form.is_valid():
            payment = payment_form.save(commit=False)
            loan_id = payment_form.cleaned_data['loan'].id  # Adjust based on how you're referencing loans
            loan = get_object_or_404(Loan, id=loan_id)
            payment.loan = loan
            payment.save()
            return redirect('member_loans', member_id=member.id)
    else:
        form = LoanForm(initial={'member': member})
        payment_form = EMIPaymentForm()

    # Calculate EMI schedule if a loan is selected
    loan_id = request.GET.get('loan_id')
    if loan_id:
        loan = get_object_or_404(Loan, id=loan_id)
        emi_schedule = loan.calculate_emi_breakdown()

    # Get the payments for each loan
    payment_history = {loan.id: loan.emi_payments.all() for loan in loans}

    return render(request, 'loans/member_loans.html', {
        'member': member,
        'loans': loans,
        'form': form,
        'emi_schedule': emi_schedule,
        'payment_form': payment_form,
        'payment_history': payment_history,
    })
