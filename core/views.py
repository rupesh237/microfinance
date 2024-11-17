from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from dashboard.mixins import RoleRequiredMixin
from django.utils import timezone

from weasyprint import HTML, CSS
from django.template.loader import get_template

from core.models import Voucher
from core.filters import VoucherFilter, ReportFilter

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
    # List of report options
    reports = [
        {'name': 'MIS Report', 'url': ''},
        {'name': 'Receipt Compile', 'url': 'receipt'},
        {'name': 'Payment Compile', 'url': 'payment'},
        # Add more reports as needed
    ]
    return render(request, 'reports/report-list.html', {'reports': reports})


# Receipt Report
def receipt_compile_report(request):
    today = timezone.now()
    
    # Check if there are any filters applied (if there are any GET parameters)
    filters_applied = bool(request.GET)
    
    # Initialize the receipts queryset and filter accordingly
    receipts = Voucher.objects.filter(voucher_type='Receipt')
    receipt_filter = ReportFilter(
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
                counter = 1
                for code, _ in SAVING_ACCOUNT_TYPE:
                    for receipt in receipt_filter.qs:
                        for statement in receipt.voucher_statement.all():
                            if statement.account.account_type == code:
                                center = statement.member.center
                                account_type = statement.account.account_type_display
                                # Initialize nested dictionaries if not already present
                                if account_type not in saving_receipts:
                                    saving_receipts[account_type] = {'total': 0}

                                if center not in saving_receipts[account_type]:
                                    saving_receipts[account_type][center] = {'SNo': counter, 'amount': 0}
                                    counter += 1

                                # Accumulate the amount for this center and account type
                                saving_receipts[account_type][center]['amount'] += receipt.amount

                                # Accumulate the total amount for this account_type
                                saving_receipts[account_type]['total'] += receipt.amount

                total_savings = sum(
                                center_data['amount']
                                for account_data in saving_receipts.values()
                                for center_key, center_data in account_data.items()
                                if center_key != 'total'  # Skip the total key
                            )
                # Render the HTML template for the PDF
                template = get_template('reports/receipt-compile-pdf.html')
                html_content = template.render({
                    'saving_receipts': saving_receipts,
                    'total_savings': total_savings,
                    'today': today,
                    'start_date': start_date,
                    'end_date': end_date,
                    'overall_counter': 1  # Start counter at 1
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

# Payment Report
def payment_compile_report(request):
    today = timezone.now()
    
    # Check if there are any filters applied (if there are any GET parameters)
    filters_applied = bool(request.GET)
    
    # Initialize the receipts queryset and filter accordingly
    payments = Voucher.objects.filter(voucher_type='Payment')
    payment_filter = ReportFilter(
        request.GET if filters_applied else None, 
        queryset=payments if filters_applied else Voucher.objects.none()
    )

    # Check if form is submitted to generate the PDF
    if filters_applied:
        # Check if filters are valid (e.g., start and end date are present)
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            # Ensure data exists for the selected filters
            if payment_filter.qs.exists():
                # Data exists, proceed with preparing data for the PDF
                saving_payments = {}
                counter = 1
                for code, _ in SAVING_ACCOUNT_TYPE:
                    for payment in payment_filter.qs:
                        for statement in payment.voucher_statement.all():
                            if statement.account.account_type == code:
                                center = statement.member.center
                                account_type = statement.account.account_type_display
                                # Initialize nested dictionaries if not already present
                                if account_type not in saving_payments:
                                    saving_payments[account_type] = {'total': 0}

                                if center not in saving_payments[account_type]:
                                    saving_payments[account_type][center] = {'SNo': counter, 'amount': 0}
                                    counter += 1

                                # Accumulate the amount for this center and account type
                                saving_payments[account_type][center]['amount'] += payment.amount

                                # Accumulate the total amount for this account_type
                                saving_payments[account_type]['total'] += payment.amount

                total_savings = sum(
                                center_data['amount']
                                for account_data in saving_payments.values()
                                for center_key, center_data in account_data.items()
                                if center_key != 'total'  # Skip the total key
                            )
                # Render the HTML template for the PDF
                template = get_template('reports/payment-compile-pdf.html')
                html_content = template.render({
                    'saving_payments': saving_payments,
                    'total_savings': total_savings,
                    'today': today,
                    'start_date': start_date,
                    'end_date': end_date,
                    'overall_counter': 1  # Start counter at 1
                })

                # Generate the PDF from the HTML content
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="payment_{start_date}-{end_date}.pdf"'
                HTML(string=html_content, base_url=request.build_absolute_uri('/')).write_pdf(response)
                return response
            else:
                # No data exists for the given filters
                messages.error(request, 'No data found for the selected filters.')
                return render(request, 'reports/payment-compile.html', {'filter': payment_filter})
        else:
            # If no valid filters are provided, return to the form
            messages.error(request, 'Please select a valid start and end date.')
            return render(request, 'reports/payment-compile.html', {'filter': payment_filter})

    return render(request, 'reports/payment-compile.html', {'filter': payment_filter})


# DayBook Report
def day_book_report(request):
    today = timezone.now().date()
    
    day_book = Voucher.objects.filter(created_at__iexact=today).all()