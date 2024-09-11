# savings/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import SavingsAccount, FixedDeposit, RecurringDeposit
from .forms import SavingsAccountForm, FixedDepositForm, RecurringDepositForm
from dashboard.models import Member

def member_savings(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    savings_accounts = SavingsAccount.objects.filter(member=member)
    fixed_deposits = FixedDeposit.objects.filter(member=member)
    recurring_deposits = RecurringDeposit.objects.filter(member=member)
    
    return render(request, 'savings/member_savings.html', {
        'member': member,
        'savings_accounts': savings_accounts,
        'fixed_deposits': fixed_deposits,
        'recurring_deposits': recurring_deposits,
    })

def add_savings_account(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == 'POST':
        form = SavingsAccountForm(request.POST)
        if form.is_valid():
            savings_account = form.save(commit=False)
            savings_account.member = member
            savings_account.save()
            return redirect('member_savings', member_id=member_id)
    else:
        form = SavingsAccountForm()
    
    return render(request, 'savings/add_savings_account.html', {
        'form': form,
        'member': member
    })

def add_fixed_deposit(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == 'POST':
        form = FixedDepositForm(request.POST)
        if form.is_valid():
            fixed_deposit = form.save(commit=False)
            fixed_deposit.member = member
            fixed_deposit.save()
            return redirect('member_savings', member_id=member_id)
    else:
        form = FixedDepositForm()
    
    return render(request, 'savings/add_fixed_deposit.html', {
        'form': form,
        'member': member
    })

def add_recurring_deposit(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == 'POST':
        form = RecurringDepositForm(request.POST)
        if form.is_valid():
            recurring_deposit = form.save(commit=False)
            recurring_deposit.member = member
            recurring_deposit.save()
            return redirect('member_savings', member_id=member_id)
    else:
        form = RecurringDepositForm()
    
    return render(request, 'savings/add_recurring_deposit.html', {
        'form': form,
        'member': member
    })
