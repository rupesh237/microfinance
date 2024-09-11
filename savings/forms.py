# savings/forms.py
from django import forms
from .models import SavingsAccount, FixedDeposit, RecurringDeposit

class SavingsAccountForm(forms.ModelForm):
    class Meta:
        model = SavingsAccount
        fields = ['account_number', 'balance']

class FixedDepositForm(forms.ModelForm):
    class Meta:
        model = FixedDeposit
        fields = ['amount', 'interest_rate', 'maturity_date']

class RecurringDepositForm(forms.ModelForm):
    class Meta:
        model = RecurringDeposit
        fields = ['amount', 'duration', 'interest_rate']
