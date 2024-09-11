
from django.shortcuts import render, get_object_or_404, redirect
from .models import Loan
from .forms import LoanForm
from dashboard.models import Member

def member_loans(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    loans = member.loans.all()

    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.member = member
            loan.save()
            return redirect('member_loans', member_id=member.id)
    else:
        form = LoanForm(initial={'member': member})

    return render(request, 'loans/member_loans.html', {
        'member': member,
        'loans': loans,
        'form': form,
    })
