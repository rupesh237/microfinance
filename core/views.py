from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from dashboard.mixins import RoleRequiredMixin
from django.utils import timezone
import datetime

from  django.conf import settings
import os

from weasyprint import HTML, CSS
from django.template.loader import get_template


from core.models import Voucher

from core.filters import VoucherFilter

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
def receipt_report_function(request, date):
    branch = request.user.profile.branch
    selected_date = timezone.make_aware(datetime.datetime.combine(date, datetime.time.min))
    a_months_ago = selected_date - datetime.timedelta(days=30)
    receipts_list = []

    receipts_list = Receipt.objects.filter(branch=branch, date__gte=a_months_ago, date__lte=selected_date)
    receipt_types = [
        "SALE", "SERVICE PROVIDED", "DUE", "OTHER", 
    ]
    dict_receipts = {receipt_type: list(receipts_list.filter(type=receipt_type)) for receipt_type in receipt_types}
    dict_receipt_totals = {f"total_{key}": sum([r.total for r in value]) for key, value in dict_receipts.items()}
    dict_receipt_dues = {f"total_{key}_due": sum([r.due_amount for r in value]) for key, value in dict_receipts.items()}
    combined_totals = {**dict_receipt_totals, **dict_receipt_dues} 
    # Accessing specific totals
    service_provided_total = dict_receipt_totals.get('total_SERVICE PROVIDED', 0)
    service_provided_due = dict_receipt_dues.get('total_SERVICE PROVIDED_due', 0)

    total_sum_receipt = sum(dict_receipt_totals.values())
    total_due_receipt = sum(dict_receipt_dues.values())

    return {
        'receipts_list': list(receipts_list),
        'selected_date': selected_date,
        'sale_list': dict_receipts.get("SALE", []),
        'service_provided_list': dict_receipts.get("SERVICE PROVIDED", []),
        'receipt_due_list': dict_receipts.get("DUE", []),
        'other_receipt_list': dict_receipts.get("OTHER", []),
        'service_provided_total': service_provided_total,
        'service_provided_due': service_provided_due,
        'total_sum_receipt': total_sum_receipt,
        'total_due_receipt': total_due_receipt,
        'dict_receipt_totals': dict_receipt_totals,
        'dict_receipt_dues': dict_receipt_dues,
    }


def receipt_report(request):
    if request.method == 'POST':
        date_str = request.POST.get("date")
        try:
            date = datetime.datetime.strptime(date_str, "%m/%d/%Y").date()
        except (ValueError, TypeError):
            return render(request, "report/receipt_report.html", {"error_message": "Invalid date format. Use MM/DD/YYYY."})
    else:
        date_str = request.GET.get("date")
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.datetime.now().date()
        except (ValueError, TypeError):
            return render(request, "report/receipt_report.html", {"error_message": "Invalid date format. Use YYYY-MM-DD."})

    context = receipt_report_function(request, date)
    context['date_formated'] = date.strftime("%m/%d/%Y")
    return render(request, "report/receipt_report.html", context)




def receipt_report_pdf_download(request, date):
    # Ensure 'date' is correctly retrieved
    date = request.GET.get("date") or date
    try:
        date_obj = datetime.datetime.strptime(date, '%m/%d/%Y').date()
    except ValueError:
        return HttpResponseBadRequest("Invalid date format. Please use MM/DD/YYYY.")

    report_data = receipt_report_function(request, date_obj)
    
    try:
        context = {
            'pagesize': 'A4',
            "mediaroot": settings.MEDIA_ROOT,
            "receipts_list": report_data['receipts_list'],
            "selected_date": report_data['selected_date'],
            'sale_list': report_data['sale_list'],
            'service_provided_list': report_data['service_provided_list'],
            'receipt_due_list': report_data['receipt_due_list'],
            'other_receipt_list': report_data['other_receipt_list'],
            'service_provided_total': report_data['service_provided_total'],
            'service_provided_due': report_data['service_provided_due'],
            'total_sum_receipt': report_data['total_sum_receipt'],
            'total_due_receipt': report_data['total_due_receipt'],
            'dict_receipt_totals': report_data['dict_receipt_totals'],
            'dict_receipt_dues': report_data['dict_receipt_dues'],
        }

        html_template = get_template("report/receipt_report_pdf.html")
        rendered_html = html_template.render(context).encode(encoding="UTF-8")
        css_files = [
            CSS(os.path.join(settings.STATIC_ROOT, 'css', 'mf.css')),
            CSS(os.path.join(settings.STATIC_ROOT, 'css', 'pdf_stylesheet.css'))
        ]

        pdf_file = HTML(string=rendered_html).write_pdf(stylesheets=css_files)

        response = HttpResponse(pdf_file, content_type='application/pdf')
        a_months_ago = date_obj - datetime.timedelta(days=30)
        filename = f"receipt-report ({a_months_ago} to {date_obj}).pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    except Exception as err:
        return HttpResponse(f'Error generating PDF: {err}', status=500)

def generate_pdf_receipt(request, receipt_id):
    # Get the receipt data (replace this with your model and logic)
    receipt = get_object_or_404(Receipt, id=receipt_id)

    # Render the HTML template with receipt data
    html_content = render(request, 'receipt_template.html', {'receipt': receipt}).content.decode()

    # Generate the PDF
    pdf = HTML(string=html_content).write_pdf()

    # Return the PDF in a response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="receipt_{receipt_id}.pdf"'
    return response

import tempfile
def generate_pdf_receipt(request, receipt_id):
    receipt = get_object_or_404(Receipt, id=receipt_id)

    # Render the HTML for the PDF
    html_content = render(request, 'receipt_template.html', {'receipt': receipt}).content.decode()
    
    # Create a temporary file to store the PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf_path = tmp_pdf.name
        HTML(string=html_content).write_pdf(pdf_path)
    
    # Pass the path of the generated PDF to the template
    return render(request, 'display_pdf.html', {'pdf_url': pdf_path, 'receipt_id': receipt_id})