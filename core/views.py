from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from dashboard.mixins import RoleRequiredMixin
from django.utils import timezone
import datetime

from  django.conf import settings
import os

from weasyprint import HTML, CSS
from django.template.loader import get_template

from core.models import Voucher
from core.filters import VoucherFilter, ReceiptFilter

from savings.models import SAVING_ACCOUNT_TYPE

# Create your views here.
def voucher_list(request):
    vouchers = Voucher.objects.all()
    # Check if there are any GET parameters (filters applied)
    filters_applied = bool(request.GET)
    today = timezone.now().date()


    voucher_filter = VoucherFilter(
        request.GET,
        queryset=vouchers if filters_applied else Voucher.objects.filter(created_at__date=today).all()
    )
    context = {
               'filter': voucher_filter,
               'today': today.strftime("%Y/%m/%d"),
               }
    if request.htmx:
        return render(request, 'vouchers/partials/voucher-container.html', context)
    return render(request, 'vouchers/voucher-list.html', context)

def report_list(request):
    return render(request, 'reports/report-list.html')


# Receipt Report
def receipt_compile_report(request):
    today = timezone.now()
    
    # Check if there are any filters applied (if there are any GET parameters)
    filters_applied = bool(request.GET)
    
    # Initialize the receipts queryset and filter accordingly
    receipts = Voucher.objects.filter(voucher_type='Receipt')
    receipt_filter = ReceiptFilter(
        request.GET if filters_applied else None, 
        queryset=receipts if filters_applied else Voucher.objects.none()
    )

    # Check if form is submitted to generate the PDF
    if filters_applied:
        # Check if filters are valid (e.g., start and end date are present)
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            # Ensure data exists for the selected filters
            if receipt_filter.qs.exists():
                # Data exists, proceed with preparing data for the PDF
                saving_receipts = {}
                for code, _ in SAVING_ACCOUNT_TYPE:
                    for receipt in receipt_filter.qs:
                        for statement in receipt.voucher_statement.all():
                            if statement.account.account_type == code:
                                center = statement.member.center
                                account_type = statement.account.account_type_display
                                if account_type not in saving_receipts:
                                    saving_receipts[account_type] = {'center': center, 'amount': 0}
                                saving_receipts[account_type]['amount'] += receipt.amount

                total_savings = sum(saving['amount'] for saving in saving_receipts.values())

                # Render the HTML template for the PDF
                template = get_template('reports/receipt-compile-pdf.html')
                html_content = template.render({
                    'saving_receipts': saving_receipts,
                    'total_savings': total_savings,
                    'today': today,
                    'start_date': start_date,
                    'end_date': end_date,
                })

                # Generate the PDF from the HTML content
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="receipt_{start_date}-{end_date}.pdf"'
                HTML(string=html_content, base_url=request.build_absolute_uri('/')).write_pdf(response)
                return response
            else:
                # No data exists for the given filters
                messages.error(request, 'No data found for the selected filters.')
                return render(request, 'reports/receipt-compile.html', {'filter': receipt_filter})
        else:
            # If no valid filters are provided, return to the form
            messages.error(request, 'Please select a valid start and end date.')
            return render(request, 'reports/receipt-compile.html', {'filter': receipt_filter})

    return render(request, 'reports/receipt-compile.html', {'filter': receipt_filter})
