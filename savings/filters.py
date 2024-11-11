from django_filters import FilterSet, ModelChoiceFilter, DateFilter
from django import forms
from .models import Statement, SavingsAccount, SAVING_ACCOUNT_TYPE

class StatementFilter(FilterSet):
    account_type = ModelChoiceFilter(
        queryset=SavingsAccount.objects.none(),
        field_name="account",
        empty_label="Select One...",
        label="Account Type",
    )
    start_date = DateFilter(
        field_name="date",
        lookup_expr="gte",
        label="From",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    end_date = DateFilter(
        field_name="date",
        lookup_expr="lte",
        label="To",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def __init__(self, *args, **kwargs):
        member_id = kwargs.pop('member_id', None)
        super().__init__(*args, **kwargs)
        
        if member_id is not None:
             # Dynamically set queryset for account_type based on member_id
            self.filters['account_type'].queryset = SavingsAccount.objects.filter(member_id=member_id)

    class Meta:
        model = Statement
        fields = ('account_type', 'start_date', 'end_date')