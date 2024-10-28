
from django import forms
from .models import Loan, EMIPayment

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['loan_type', 'amount', 'interest_rate', 'duration_months', 'start_date', 'end_date', 'status']


class EMIPaymentForm(forms.ModelForm):
    class Meta:
        model = EMIPayment
        fields = ['loan', 'amount_paid']

