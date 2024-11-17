import django_filters
from django import forms
from django.contrib.auth.models import User

from django.utils import timezone

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

class ReportFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name="created_at__date",
        lookup_expr="gte",
        label="From",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    end_date = django_filters.DateFilter(
        field_name="created_at__date",
        lookup_expr="lte",
        label="To",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    staff = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name="created_by",
        empty_label="All",
        label="Staff",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        today = timezone.now().date()  
        self.filters['start_date'].field.initial = today
        self.filters['end_date'].field.initial = today

    class Meta:
        model = Voucher
        fields = ('start_date', 'end_date', 'staff')
