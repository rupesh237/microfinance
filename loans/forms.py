
from django import forms
from django.forms.widgets import DateInput
from .models import Loan, EMIPayment

from django.utils.timezone import now

class LoanDemandForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['loan_type', 'loan_purpose', 'amount', 'loan_demand_date', 'loan_disburse_date']

        widgets = {
            'loan_demand_date': DateInput(attrs={'type': 'date'}),
            'loan_disburse_date': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['loan_demand_date'].initial = now().date()  # Current date
        self.fields['loan_disburse_date'].initial = now().date()

class LoanAnalysisForm(forms.ModelForm):
    
    class Meta:
        model = Loan
        fields = ['loan_analysis_amount', 'loan_analysis_date', 'approved_date']

        widgets = {
            'loan_analysis_date': DateInput(attrs={'type': 'date'}),
            'approved_date': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # Expecting an instance of Loan to be passed through kwargs
        loan_instance = kwargs.pop('loan_instance', None)
        super().__init__(*args, **kwargs)
        
        # Set initial values
        if loan_instance:
            self.fields['loan_analysis_amount'].initial = loan_instance.amount
        self.fields['loan_analysis_date'].initial = now().date()  # Current date
        self.fields['approved_date'].initial = now().date()

class LoanDisburseForm(forms.ModelForm):
    
    class Meta:
        model = Loan
        fields = ['loan_type', 'amount', 'interest_rate', 'duration_months']

    def __init__(self, *args, **kwargs):
        # Expecting an instance of Loan to be passed through kwargs
        loan_instance = kwargs.pop('loan_instance', None)
        super().__init__(*args, **kwargs)
        
        # Set initial values
        if loan_instance:
            self.fields['loan_type'].initial = loan_instance.loan_type
            self.fields['amount'].initial = loan_instance.amount




class EMIPaymentForm(forms.ModelForm):
    class Meta:
        model = EMIPayment
        fields = ['loan', 'amount_paid']

