import django_filters
from django import forms
from django.contrib.auth.models import User

from django.utils import timezone

from core.models import Voucher
from dashboard.models import Center

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

class CollectionSheetFilter(django_filters.FilterSet):
    date = django_filters.CharFilter(
        method='filter_by_date',  # Custom filtering method
        label="Apply Date",
        widget=forms.DateInput(attrs={"type": "date"}),  # HTML5 date input widget
    )

    class Meta:
        model = Center
        fields = ('date',)

    def filter_by_date(self, queryset, name, value):
        """
        Filters centers where `meeting_date` matches the day of the given date.
        The `meeting_date` field stores only the day of the month.
        """
        if value:
            try:
                # Extract the day from the date (e.g., 2024-12-04 => day = 4)
                day = int(value.split('-')[2])  # Get the day part of the date string
                return queryset.filter(meeting_date=day)
            except ValueError:
                # Handle invalid date format
                return queryset.none()
        return queryset

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

     # New date filter based on the transaction_date field (or any other date field you have)
    date = django_filters.DateFilter(
        field_name="transaction_date",  # Change this to your date field
        lookup_expr="exact",  # You can change this to gte, lte, or range depending on your needs
        label="Date",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        today = timezone.now().date()  
        self.filters['start_date'].field.initial = today
        self.filters['end_date'].field.initial = today
        self.filters['date'].field.initial = today

    class Meta:
        model = Voucher
        fields = ('start_date', 'end_date', 'staff', 'date')
