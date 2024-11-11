# savings/forms.py
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import SavingsAccount, SAVING_ACCOUNT_TYPE, CURRENT_ACCOUNT_TYPE, FixedDeposit, RecurringDeposit, CashSheet, PaymentSheet

class SavingsAccountForm(forms.ModelForm):
    created_date_display = forms.DateTimeField(label="Effective Date", required=False, 
                                              widget=forms.DateTimeInput(format='%Y-%m-%d', attrs={'readonly': 'readonly'},))
    class Meta:
        model = SavingsAccount
        fields = ['account_type', 'created_date_display', 'interest_rate', 'amount']

    def __init__(self, *args, **kwargs):
        self.member = kwargs.pop('member', None) 
        super(SavingsAccountForm, self).__init__(*args, **kwargs)
        # Disable only the 'every' field
        self.fields['interest_rate'].disabled = True
        self.fields['created_date_display'].disabled = True

        # If editing an existing center, use the saved formed_date value (formatted to date only)
        if self.instance and self.instance.pk:
            self.fields['created_date_display'].initial = self.instance.formed_date.date()
        else:
            self.fields['created_date_display'].initial = timezone.now().date()

    def clean(self):
        cleaned_data = super().clean()
        account_type = cleaned_data.get('account_type')
        print(account_type)

        # Check if an account with the selected account_type already exists for the given member
        if SavingsAccount.objects.filter(account_type=account_type, member=self.member).exists():
            raise ValidationError(f"An account with type '{account_type}' already exists for this member.")
        
        return cleaned_data
    
class CashSheetForm(forms.ModelForm):
    class Meta:
        model = CashSheet
        fields = ['deposited_by', 'remarks', 'source_of_fund']

    def __init__(self, *args, **kwargs):
        member = kwargs.pop('member', None)
        super().__init__(*args, **kwargs)

        # Initialize account_amount_fields as an empty list
        self.account_amount_fields = []
        
        # Retrieve accounts associated with the member
        accounts = SavingsAccount.objects.filter(member=member)
        for account in accounts:
            # Create a unique name for the amount field for each account
            amount_field_name = f'amount_{account.id}'

            # Define form fields for the account
            self.fields[amount_field_name] = forms.DecimalField(
                label=f'Amount for {account.account_number}',
                required=False
            )

            # Append a tuple for later use in the template if needed
            self.account_amount_fields.append((account, amount_field_name))


class PaymentSheetForm(forms.ModelForm):
    class Meta:
        model = PaymentSheet
        fields = ['withdrawn_by', 'remarks', 'cheque_no']

    def __init__(self, *args, **kwargs):
        member = kwargs.pop('member', None)
        super().__init__(*args, **kwargs)

        # Initialize account_amount_fields as an empty list
        self.account_amount_fields = []
        
        # Extract only the codes for filtering
        current_account_codes = [code for code, _ in CURRENT_ACCOUNT_TYPE]

        accounts = SavingsAccount.objects.filter(member=member)
        current_accounts = [account for account in accounts if account.account_type in current_account_codes]
        for account in current_accounts:
            # Create a unique name for the amount field for each account
            amount_field_name = f'amount_{account.id}'

            # Define form fields for the account
            self.fields[amount_field_name] = forms.DecimalField(
                label=f'Amount for {account.account_number}',
                required=False
            )

            # Append a tuple for later use in the template if needed
            self.account_amount_fields.append((account, amount_field_name))


class FixedDepositForm(forms.ModelForm):
    class Meta:
        model = FixedDeposit
        fields = ['amount', 'interest_rate', 'maturity_date']

class RecurringDepositForm(forms.ModelForm):
    class Meta:
        model = RecurringDeposit
        fields = ['amount', 'duration', 'interest_rate']
