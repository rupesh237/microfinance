import django_filters
from django import forms
from core.models import Voucher

class VoucherFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(
        field_name="created_at__date",
        lookup_expr="iexact",
        label="Apply Date",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = Voucher
        fields = ('date',)