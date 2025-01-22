from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.forms import modelformset_factory
from django.db.models import Count
from django.db import transaction
from django.urls import reverse
from django.template.loader import render_to_string

from dashboard.mixins import RoleRequiredMixin
from django.utils import timezone
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from weasyprint import HTML, CSS
from django.template.loader import get_template

from core.models import Voucher, CollectionSheet, Teller, CashVault, VaultTransaction, TellerToTellerTransaction
from core.forms import CollectionSheetForm
from core.filters import VoucherFilter, ReportFilter, CollectionSheetFilter

from dashboard.models import Center, GRoup, Member, User
from savings.models import SAVING_ACCOUNT_TYPE, SavingsAccount, CashSheet, Statement
from loans.models import Loan, LOAN_TYPE_CHOICES

from collections import defaultdict

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
                loan_receipts = {}
                counter = 1

                # Process loan receipts
                for code, _ in LOAN_TYPE_CHOICES:
                    for receipt in receipt_filter.qs:
                        if receipt.category == 'Loan':  # Filter only loan receipts
                            for emi in receipt.emi_payments.all():  # Iterate over EMI payments
                                loan_type = emi.loan.loan_type
                                center = emi.loan.member.center
                                loan_type_display = emi.loan.get_loan_type_display()

                                # Initialize nested dictionaries if not already present
                                if loan_type_display not in loan_receipts:
                                    loan_receipts[loan_type_display] = {'total': 0}

                                if center not in loan_receipts[loan_type_display]:
                                    loan_receipts[loan_type_display][center] = {'SNo': counter, 'amount': 0}
                                    counter += 1

                                # Accumulate the amount for this center and loan type
                                loan_receipts[loan_type_display][center]['amount'] += receipt.amount

                                # Accumulate the total amount for this loan type
                                loan_receipts[loan_type_display]['total'] += receipt.amount

                total_loans = sum(
                    center_data['amount']
                    for loan_data in loan_receipts.values()
                    for center_key, center_data in loan_data.items()
                    if center_key != 'total'  # Skip the total key
                )

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
                
                grand_total = total_loans + total_savings

                # print("Saving Receipts:", saving_receipts)
                # print("Loan Receipts:", loan_receipts)
                # print("Total Savings:", total_savings)
                # print("Total Loans:", total_loans)
                # print("Grand Total:", grand_total)
                # Render the HTML template for the PDF
                template = get_template('reports/receipt-compile-pdf.html')
                html_content = template.render({
                    'saving_receipts': saving_receipts,
                    'loan_receipts': loan_receipts,
                    'grand_total': grand_total,
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


# Collection Sheet
def collection_sheet_by_date(request):
    today = timezone.now()
    day = today.day

    centers = Center.objects.annotate(group_count=Count('groups')).filter(group_count__gt=0).order_by('meeting_date')
    
    # Check if there are any GET parameters (filters applied)
    filters_applied = bool(request.GET)
    selected_date = request.GET.get('date')  # e.g., '2024-06-10'
    if selected_date:
        try:
            selected_date = timezone.datetime.strptime(selected_date, "%Y-%m-%d").date()
        except ValueError:
            selected_date = today.date()  # Default to today if the date is invalid
    else:
        selected_date = today.date()
    
    meetings_filter = CollectionSheetFilter(
        request.GET,
        queryset=centers if filters_applied else Center.objects.filter(meeting_date=day).all()
    )

    # Check if CollectionSheets already exist for today
    centers_with_sheets = {}
    for center in centers:
        formatted_date = date(today.year, today.month, center.meeting_date)
        sheets = CollectionSheet.objects.filter(
            center=center,
            meeting_date=formatted_date
        ).first()
        centers_with_sheets[center.id] = sheets

    context = {
               'filter': meetings_filter,
               'centers_with_sheets': centers_with_sheets,
               'selected_date': selected_date.strftime("%Y-%m-%d"),
               'today': today.strftime("%Y/%m/%d"),
               }
    if request.htmx:
        return render(request, 'collection-sheet/partials/collection-sheet-container.html', context)
    return render(request, 'collection-sheet/collection-sheet-by-date.html', context)

def collection_sheet_by_center(request):
    today = date.today()
    centers = Center.objects.annotate(group_count=Count('groups')).filter(group_count__gt=0).order_by('meeting_date')
    # Check if CollectionSheets already exist for today
    centers_with_sheets = {}
    for center in centers:
        formatted_date = date(today.year, today.month, center.meeting_date)
        sheets = CollectionSheet.objects.filter(
            center=center,
            meeting_date=formatted_date
        ).first()
        centers_with_sheets[center.id] = sheets

    context = {
               'centers': centers,
               'centers_with_sheets': centers_with_sheets,
               }
    return render(request, 'collection-sheet/collection-sheet-by-center.html', context)

def create_collection_sheet(request, center_id):
    center = get_object_or_404(Center, id=center_id)
    groups = center.groups.all()  # Assuming groups are related to the Center model
    members = Member.objects.filter(group__in=groups)

    # meeting_no
    latest_sheet = CollectionSheet.objects.filter(center=center).last()
    if latest_sheet:
        meeting_no = latest_sheet.meeting_no + 1
    else:
        meeting_no = 1

    today = date.today()
    meeting_date = center.meeting_date
    formatted_date = date(today.year, today.month, meeting_date)
    # Add one month to the formatted_date
    upcoming_meeting_date = formatted_date + relativedelta(months=1)

    # Fetch unique account types along with their display names
    savings_accounts = SavingsAccount.objects.filter(member__in=members)
    account_types = SavingsAccount.objects.filter(
    member__in=members
    ).with_account_type_order().values_list('account_type', flat=True).distinct()
    account_type_display = [
        {'key': atype, 'display': savings_accounts.filter(account_type=atype).first().account_type_display}
        for atype in account_types
    ]

    loans = Loan.objects.filter(member__in=members)
    loan_types = Loan.objects.filter(member__in=members).values_list('loan_type', flat=True).distinct()
    # Convert to a sorted list for consistent header ordering
    loan_types = sorted(set(loan_types))

    # Generate initial data for members
    initial_data = []
    for member in members:
        savings_accounts = SavingsAccount.objects.filter(member=member).with_account_type_order()
        # Structure account details as a dictionary with both amount and balance
        account_details = {
            account.account_type: {
                'amount': account.amount,
                'balance': account.balance,
            }
            for account in savings_accounts
        }

        loans = Loan.objects.filter(member=member)
        loan_details = {
            loan.loan_type: {
                'installment_no': loan.get_installment_number(),
                'installment_amount': loan.installement_amount,
            }
            for loan in loans
        }

        # Calculate total savings and loan installments
        total_savings = sum(account.amount for account in savings_accounts)
        total_loan_installment = sum(loan.installement_amount for loan in loans)

        # Add calculated total amount to be paid
        total_amount_to_pay = total_loan_installment + total_savings  # Customize as needed

        initial_data.append({
            'member': member,
            'member_collection': 0.0, 
            'total': total_amount_to_pay,
            'special_record': 'P', 
            'account_details': account_details,
            'loan_details': loan_details,
            'loans':loans,
        })

    CollectionSheetFormset = modelformset_factory(
        CollectionSheet,
        form=CollectionSheetForm,
        extra=len(initial_data),
    )

    total_columns = 4 + (len(account_types) * 2) + (len(loan_types) * 2)
    # Group initial data by group
    grouped_data = defaultdict(list)
    for data in initial_data:
        grouped_data[data['member'].group].append(data)

    # Calculate totals for each group
    group_totals = {group: sum(item['total'] for item in data) for group, data in grouped_data.items()}
    # Calculate overall total for all groups
    all_groups_total = sum(group_totals.values())

    # Combine forms with grouped data
    combined_data = []
    formset = CollectionSheetFormset(queryset=CollectionSheet.objects.none(), initial=initial_data)
    for (group, group_data) in grouped_data.items(): 
        combined_data.append({
            'groups': {
                group: {
                    'data': group_data,
                    'total': group_totals[group],
                }
            }
        })

    # Initialize variables to hold the total amounts for savings and loans
    overall_total_savings = {
        account_type['key']: {'amount': 0, 'balance': 0}
        for account_type in account_type_display
    }
    overall_total_loans = {loan_type: {'installment_amount': 0} for loan_type in loan_types}

    # Loop through the combined_data to calculate the totals
    for item in combined_data:
        for group, group_data in item['groups'].items():
            for item in group_data['data']:
                # Add up savings totals
                for account_type in account_type_display:
                    account_details = item['account_details'].get(account_type['key'], {})
                    
                    # Extract amount and balance (default to 0 if missing)
                    account_amount = account_details.get('amount', 0)
                    account_balance = account_details.get('balance', 0)
                    
                    # Add to total_savings for the corresponding account type
                    overall_total_savings[account_type['key']]['amount'] += account_amount
                    overall_total_savings[account_type['key']]['balance'] += account_balance
                
                # Add up loan totals
                for loan_type in loan_types:
                    loan_amount = item['loan_details'].get(loan_type, {}).get('installment_amount', 0)
                    overall_total_loans[loan_type]['installment_amount'] += loan_amount

    if request.method == "POST":
        # print("Request POST data:", request.POST)
        formset = CollectionSheetFormset(request.POST, initial=initial_data)

        if formset.is_valid():
            # Retrieve extra fields from POST
            status = request.POST.get('status', 'preview')
            evaluation_no = request.POST.get('evaluation_no')
            meeting_by = request.POST.get('meeting_by')
            supervision_by_1 = request.POST.get('supervision_by_1')
            supervision_by_2 = request.POST.get('supervision_by_2')
            next_meeting_date = request.POST.get('next_meeting_date', upcoming_meeting_date)
            total = request.POST.get('total', 0.0)
            # print(f"Total: {total}")
            
            if status == 'saved':
                for form, data in zip(formset, initial_data):
                    if form.cleaned_data:  # Only process valid, non-empty forms
                        member_collection = form.cleaned_data.get('member_collection')
                        special_record = form.cleaned_data.get('special_record')
                        member = data['member']  # Get the member object from `initial_data`

                        if member_collection and special_record and member:
                            try: 
                                with transaction.atomic():  # Start a database transaction
                                    # Create a new CashSheet instance for each account
                                    collection_sheet = CollectionSheet(
                                        member = data['member'],
                                        member_collection = member_collection,
                                        special_record = special_record,
                                        evaluation_no = evaluation_no,
                                        meeting_by = User.objects.get(id=meeting_by),
                                        supervision_by_1 = User.objects.get(id=supervision_by_1),
                                        supervision_by_2 = User.objects.get(id=supervision_by_2), 
                                        meeting_date = formatted_date,
                                        next_meeting_date = next_meeting_date,
                                        center = center,
                                        branch = center.branch,
                                        total = total,
                                        status = status.capitalize(),
                                    )
                                    collection_sheet.save()
                                messages.success(request, f"Collection sheet saved successfully.")
                            except Exception as e:
                                print(f"Error creating CollectionSheet: {e}")
                                messages.error(request, f"Error saving collection sheet for member {member.name}")
                return redirect(f"{reverse('collection_sheet', kwargs={'center_id': center.id})}?meeting_date={formatted_date}")
        else:
            print("Formset errors:", formset.errors)
    else:
        formset = CollectionSheetFormset(queryset=CollectionSheet.objects.none(), initial=initial_data)

    context = {
        'formset': formset, 
        'center': center, 
        'users':User.objects.all(),
        'meeting_no': meeting_no,
        'meeting_date': formatted_date.strftime("%Y-%m-%d"),
        'next_meeting_date': upcoming_meeting_date.strftime("%Y-%m-%d") ,
        'combined_data': combined_data,
        'all_groups_total': all_groups_total,
        'overall_total_savings': overall_total_savings,
        'overall_total_loans': overall_total_loans,
        'account_types': account_type_display,
        'loan_types': loan_types,
        'total_columns': total_columns,
    }
    return render(request, 'collection-sheet/create_collection_sheet.html', context=context)
    
def generate_voucher_number():
        today_str = timezone.now().strftime('%Y%m%d')
        last_voucher = Voucher.objects.filter(transaction_date=timezone.now().date()).order_by('voucher_number').last()
        print(f"last Voucher: {last_voucher}")
        if last_voucher:
            last_sequence = int(last_voucher.voucher_number[-3:])
            next_sequence = last_sequence + 1
        else:
            next_sequence = 1
        return f"{today_str}{next_sequence:03}"
        
def update_member_accounts(request, initial_data):
    transaction_date = timezone.now().date()
    for data in initial_data:
        member = data['member']
        savings_accounts = data['account_details']
        for account_type, details in savings_accounts.items():
            account = SavingsAccount.objects.filter(account_type=account_type, member=member).first()
            voucher_number=generate_voucher_number()
            # Create a Voucher
            try:
                with transaction.atomic(): 
                    voucher = Voucher.objects.create(
                        voucher_number=voucher_number,
                        voucher_type='Receipt',
                        category='Collection Sheet',
                        amount=details['amount'],
                        description=f'Collection Sheet of {member}: {account.account_number}',
                        transaction_date=transaction_date,
                        created_by=request.user,
                    )

                    # Update account balance
                    prev_balance = account.balance
                    account.balance += details['amount']
                    account.save()

                    # Create a Statement
                    Statement.objects.create(
                        account=account,
                        member=member,
                        transaction_type='credit',
                        category='Collection',
                        cr_amount=details['amount'],
                        prev_balance=prev_balance,
                        curr_balance=account.balance,
                        remarks='Collection Sheet Payment',
                        transaction_date=transaction_date,
                        created_by=request.user,
                        voucher=voucher,
                    )
            except Exception as e:
                print(f"Error processing account {account.account_number}: {e}")
                raise e  # Rollback on any exception


def collection_sheet_view(request, center_id):
    meeting_date_str = request.GET.get('meeting_date')  # Retrieve meeting_date from query parameters
    try:
        # Convert from YYYY/MM/DD to YYYY-MM-DD
        meeting_date_obj = datetime.strptime(meeting_date_str, "%Y/%m/%d")
        meeting_date = meeting_date_obj.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        meeting_date = datetime.strptime(meeting_date_str, "%Y-%m-%d")
    center = get_object_or_404(Center, id=center_id)

    # Filter collection sheets based on meeting_date
    collection_sheets = CollectionSheet.objects.filter(center=center, meeting_date=meeting_date).all()
    groups = center.groups.all()  # Assuming groups are related to the Center model
    members = Member.objects.filter(group__in=groups)

    # Fetch unique account types along with their display names
    savings_accounts = SavingsAccount.objects.filter(member__in=members)
    account_types = SavingsAccount.objects.filter(
    member__in=members
    ).with_account_type_order().values_list('account_type', flat=True).distinct()
    account_type_display = [
        {'key': atype, 'display': savings_accounts.filter(account_type=atype).first().account_type_display}
        for atype in account_types
    ]

    loans = Loan.objects.filter(member__in=members)
    loan_types = Loan.objects.filter(member__in=members).values_list('loan_type', flat=True).distinct()
    # Convert to a sorted list for consistent header ordering
    loan_types = sorted(set(loan_types))

    # Generate initial data for members
    # Prepare initial data with total amount calculation
    initial_data = []
    for member in members:
        # Fetch the existing collection sheet for the member
        existing_sheet = collection_sheets.filter(member=member).first()

        savings_accounts = SavingsAccount.objects.filter(member=member).with_account_type_order()
        # Structure account details as a dictionary with both amount and balance
        account_details = {
            account.account_type: {
                'amount': account.amount,
                'balance': account.balance,
            }
            for account in savings_accounts
        }

        loans = Loan.objects.filter(member=member)
        loan_details = {
            loan.loan_type: {
                'installment_no': loan.get_installment_number(),
                'installment_amount': loan.installement_amount,
            }
            for loan in loans
        }

        # Calculate total savings and loan installments
        total_savings = sum(account.amount for account in savings_accounts)
        total_loan_installment = sum(loan.installement_amount for loan in loans)

        # Add calculated total amount to be paid
        total_amount_to_pay = total_loan_installment + total_savings  # Customize as needed

        initial_data.append({
            'member': member,
            'member_collection': existing_sheet.member_collection if existing_sheet else 0.0,
            'special_record': existing_sheet.special_record if existing_sheet else 'P',
            'status': existing_sheet.status if existing_sheet else 'Saved',
            'total': total_amount_to_pay,
            'account_details': account_details,
            'loan_details': loan_details,
            'loans':loans,
        })

    CollectionSheetFormset = modelformset_factory(
        CollectionSheet,
        form=CollectionSheetForm,
        extra=len(initial_data),
    )

    total_columns = 4 + (len(account_types) * 2) + (len(loan_types) * 2)
    # Group initial data by group
    grouped_data = defaultdict(list)
    for data in initial_data:
        grouped_data[data['member'].group].append(data)

    # Calculate totals for each group
    group_totals = {group: sum(item['total'] for item in data) for group, data in grouped_data.items()}
    # Calculate overall total for all groups
    all_groups_total = sum(group_totals.values())

    # Combine forms with grouped data
    combined_data = []
    # Prepare the formset
    formset_data = [
        {
            'member': data['member'].id,
            'member_collection': data['member_collection'],
            'special_record': data['special_record'],
        }
        for data in initial_data
    ]
    # print(formset_data)
    formset = CollectionSheetFormset(queryset=CollectionSheet.objects.none(), initial=formset_data)
    for (group, group_data) in grouped_data.items(): 
        combined_data.append({
            'groups': {
                group: {
                    'data': group_data,
                    'total': group_totals[group],
                }
            }
        })


    # Initialize variables to hold the total amounts for savings and loans
    overall_total_savings = {
        account_type['key']: {'amount': 0, 'balance': 0}
        for account_type in account_type_display
    }
    overall_total_loans = {loan_type: {'installment_amount': 0} for loan_type in loan_types}

    # Loop through the combined_data to calculate the totals
    for item in combined_data:
        for group, group_data in item['groups'].items():
            for item in group_data['data']:
                # Add up savings totals
                for account_type in account_type_display:
                    account_details = item['account_details'].get(account_type['key'], {})
                    
                    # Extract amount and balance (default to 0 if missing)
                    account_amount = account_details.get('amount', 0)
                    account_balance = account_details.get('balance', 0)
                    
                    # Add to total_savings for the corresponding account type
                    overall_total_savings[account_type['key']]['amount'] += account_amount
                    overall_total_savings[account_type['key']]['balance'] += account_balance
                
                # Add up loan totals
                for loan_type in loan_types:
                    loan_amount = item['loan_details'].get(loan_type, {}).get('installment_amount', 0)
                    overall_total_loans[loan_type]['installment_amount'] += loan_amount

    # Check for previous CollectionSheet instances
    collection_sheets = CollectionSheet.objects.filter(center=center).order_by('meeting_date')

    if request.method == "POST":
        # print("Request POST data:", request.POST)
        formset = CollectionSheetFormset(request.POST, initial=initial_data, queryset=collection_sheets)

        if formset.is_valid():
            status = request.POST.get('status', 'preview')
            evaluation_no = request.POST.get('evaluation_no')
            meeting_by = request.POST.get('meeting_by')
            supervision_by_1 = request.POST.get('supervision_by_1')
            supervision_by_2 = request.POST.get('supervision_by_2')
            next_meeting_date = request.POST.get('next_meeting_date', collection_sheets[0].next_meeting_date)
            total = request.POST.get('total')
            print(f"Total: {total}")
            print(f"Status: {status}")
            
            if status == 'save':
                # Loop through each form in the formset
                print("Updating")
                for form, data in zip(formset, initial_data):
                    if form.cleaned_data:  # Only process valid, non-empty forms
                        member_collection = form.cleaned_data.get('member_collection')
                        special_record = form.cleaned_data.get('special_record')
                        member = data['member']  # Get the member object from `initial_data`

                        print(f"{member}: {member_collection}- {special_record}")
                        if member_collection and special_record and member:
                            try:
                                with transaction.atomic():  # Start transaction block
                                    member = data['member']
                                    if not member:
                                        continue  # Skip if member is missing
                                    
                                    # Fetch the existing CollectionSheet instance if it exists
                                    collection_sheet, created = CollectionSheet.objects.get_or_create(
                                        member=member,
                                        evaluation_no=evaluation_no,
                                        defaults={
                                            'member_collection': member_collection,
                                            'special_record': special_record,
                                            'meeting_by': User.objects.get(id=meeting_by),
                                            'supervision_by_1': User.objects.get(id=supervision_by_1),
                                            'supervision_by_2': User.objects.get(id=supervision_by_2),
                                            'next_meeting_date': next_meeting_date,
                                            'center': center,
                                            'branch': center.branch,
                                            'total': total,
                                            'status': data['status'],
                                        }
                                    )
                                    print(created)
                                    print(collection_sheet)

                                    if not created:  # Update fields if the record already exists
                                        collection_sheet.member_collection = member_collection
                                        collection_sheet.special_record = special_record
                                        collection_sheet.meeting_by = User.objects.get(id=meeting_by)
                                        collection_sheet.supervision_by_1 = User.objects.get(id=supervision_by_1)
                                        collection_sheet.supervision_by_2 = User.objects.get(id=supervision_by_2)
                                        collection_sheet.meeting_date = meeting_date
                                        collection_sheet.next_meeting_date = next_meeting_date
                                        collection_sheet.center = center
                                        collection_sheet.branch = center.branch
                                        collection_sheet.total = total
                                        collection_sheet.status = status.capitalize()
                                        # Save the updated instance
                                        collection_sheet.save()
                                messages.success(request, f"Collection sheet saved successfully.")
                                print("Saved successfully")
                            except Exception as e:
                                print(f"Error: {e}")
                                messages.error(request, f"Error saving collection sheet for member {member.name}")
                return redirect(f"{reverse('collection_sheet', kwargs={'center_id': center.id})}?meeting_date={meeting_date_str}")
            elif status in ['submitted', 'approved', 'accepted']:
                try:
                    if status == "accepted":
                        try:
                            update_member_accounts(request, initial_data=initial_data)
                            # If update_member_accounts succeeds, update the CollectionSheet status
                            CollectionSheet.objects.filter(center=center, meeting_date=meeting_date).update(status=status.capitalize())
                            messages.success(request, f"All collection sheets for center {center.code} have been updated to status '{status.capitalize()}'.")
                        except Exception as e:
                            print(f"Error: {e}")
                            messages.error(request, f"An error occurred while updating accounts: {e}")
                    else:
                        CollectionSheet.objects.filter(center=center, meeting_date=meeting_date).update(status=status.capitalize())
                        messages.success(request, f"All collection sheets for center {center.code} have been updated to status '{status.capitalize()}'.")
                except Exception as e:
                    print(f"Error updating collection sheets' status: {e}")
                return redirect(f"{reverse('collection_sheet', kwargs={'center_id': center.id})}?meeting_date={meeting_date_str}")
        else:
            print("Formset errors:", formset.errors)
    else:
        formset = CollectionSheetFormset(queryset=CollectionSheet.objects.none(), initial=formset_data)

    context = {
        'formset': formset, 
        'center': center, 
        'users':User.objects.all(),
        'combined_data': combined_data,
        'all_groups_total': all_groups_total,
        'overall_total_savings': overall_total_savings,
        'overall_total_loans': overall_total_loans,
        'account_types': account_type_display,
        'loan_types': loan_types,
        'total_columns': total_columns,
        'meeting_date': meeting_date,
        'meeting_no': collection_sheets[0].meeting_no,
        'status': collection_sheets[0].status,
        'evaluation_no': collection_sheets[0].evaluation_no,
        'meeting_by': collection_sheets[0].meeting_by,
        'supervision_by_1': collection_sheets[0].supervision_by_1,
        'supervision_by_2': collection_sheets[0].supervision_by_2,
        'next_meeting_date': collection_sheets[0].next_meeting_date,
        'total': collection_sheets[0].total,
    }

    return render(request, 'collection-sheet/collection-sheet-view.html', context=context)

def collection_sheet_pdf(request, center_id):
    # Fetch data for your template
    meeting_date_str = request.GET.get('meeting_date')  # Retrieve meeting_date from query parameters
    try:
        # Convert from YYYY/MM/DD to YYYY-MM-DD
        meeting_date_obj = datetime.strptime(meeting_date_str, "%Y/%m/%d")
        meeting_date = meeting_date_obj.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        meeting_date = datetime.strptime(meeting_date_str, "%Y-%m-%d")

    center = get_object_or_404(Center, id=center_id)
    groups = center.groups.all()  # Assuming groups are related to the Center model
    members = Member.objects.filter(group__in=groups)

    # Filter collection sheets based on meeting_date
    collection_sheets = CollectionSheet.objects.filter(center=center, meeting_date=meeting_date).all()
    if collection_sheets:
        meeting_no = collection_sheets[0].meeting_no
    else:
        latest_sheet = CollectionSheet.objects.filter(center=center).last()
        if latest_sheet:
            meeting_no = latest_sheet.meeting_no + 1
        else:
            meeting_no = 1

    # Fetch unique account types along with their display names
    savings_accounts = SavingsAccount.objects.filter(member__in=members)
    account_types = SavingsAccount.objects.filter(
    member__in=members
    ).with_account_type_order().values_list('account_type', flat=True).distinct()
    account_type_display = [
        {'key': atype, 'display': savings_accounts.filter(account_type=atype).first().account_type_display}
        for atype in account_types
    ]

    loans = Loan.objects.filter(member__in=members)
    loan_types = Loan.objects.filter(member__in=members).values_list('loan_type', flat=True).distinct()
    # Convert to a sorted list for consistent header ordering
    loan_types = sorted(set(loan_types))

    # Generate initial data for members
    # Prepare initial data with total amount calculation
    initial_data = []
    for member in members:
        savings_accounts = SavingsAccount.objects.filter(member=member).with_account_type_order()
        # Structure account details as a dictionary with both amount and balance
        account_details = {
            account.account_type: {
                'amount': account.amount,
                'balance': account.balance,
            }
            for account in savings_accounts
        }

        loans = Loan.objects.filter(member=member)
        loan_details = {
            loan.loan_type: {
                'installment_no': loan.get_installment_number(),
                'installment_amount': loan.installement_amount,
            }
            for loan in loans
        }

        # Calculate total savings and loan installments
        total_savings = sum(account.amount for account in savings_accounts)
        total_loan_installment = sum(loan.installement_amount for loan in loans)

        # Add calculated total amount to be paid
        total_amount_to_pay = total_loan_installment + total_savings  # Customize as needed

        initial_data.append({
            'member': member,
            'member_collection': '',
            'special_record': '',
            'status': '',
            'total': total_amount_to_pay,
            'account_details': account_details,
            'loan_details': loan_details,
            'loans':loans,
        })

    total_columns = 4 + (len(account_types) * 2) + (len(loan_types) * 2)
    # Group initial data by group
    grouped_data = defaultdict(list)
    for data in initial_data:
        grouped_data[data['member'].group].append(data)

    # Calculate totals for each group
    group_totals = {group: sum(item['total'] for item in data) for group, data in grouped_data.items()}
    # Calculate overall total for all groups
    all_groups_total = sum(group_totals.values())

    # Combine forms with grouped data
    combined_data = []
    for (group, group_data) in grouped_data.items(): 
        combined_data.append({
            'groups': {
                group: {
                    'data': group_data,
                    'total': group_totals[group],
                }
            }
        })

    # Initialize variables to hold the total amounts for savings and loans
    overall_total_savings = {
        account_type['key']: {'amount': 0, 'balance': 0}
        for account_type in account_type_display
    }
    overall_total_loans = {loan_type: {'installment_amount': 0} for loan_type in loan_types}

    # Loop through the combined_data to calculate the totals
    for item in combined_data:
        for group, group_data in item['groups'].items():
            for item in group_data['data']:
                # Add up savings totals
                for account_type in account_type_display:
                    account_details = item['account_details'].get(account_type['key'], {})
                    
                    # Extract amount and balance (default to 0 if missing)
                    account_amount = account_details.get('amount', 0)
                    account_balance = account_details.get('balance', 0)
                    
                    # Add to total_savings for the corresponding account type
                    overall_total_savings[account_type['key']]['amount'] += account_amount
                    overall_total_savings[account_type['key']]['balance'] += account_balance
                
                # Add up loan totals
                for loan_type in loan_types:
                    loan_amount = item['loan_details'].get(loan_type, {}).get('installment_amount', 0)
                    overall_total_loans[loan_type]['installment_amount'] += loan_amount

    # Render template with context data
    html_string = render_to_string('collection-sheet/collection-sheet-pdf.html', {
        'center': center,
        'meeting_no': meeting_no,
        'meeting_date': meeting_date,
        'combined_data': combined_data,
        'account_types': account_type_display,
        'loan_types': loan_types,
        'all_groups_total': all_groups_total,
        'overall_total_savings':overall_total_savings,
        'overall_total_loans': overall_total_loans,
        'total_columns':total_columns,
    })

    # Create PDF response
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'inline; filename="collectionsheet_{center.code}_{meeting_date}.pdf"'

    # Generate PDF
    HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(response)

    return response

# CASH MANAGEMET #
from decimal import Decimal
def create_vault_transaction(request, vault, teller, transaction_type, amount):
    # print(f"Branch: {vault.branch}")
    if transaction_type == 'Deposit':
        if Decimal(amount) > teller.balance:
            messages.error(request, f'Insufficient balance with {teller}.')
            return None
        
        try:
            transaction = VaultTransaction.objects.create(
                branch = vault.branch,
                transaction_type=transaction_type,
                cash_vault=vault, 
                teller=teller,
                amount=amount,
                )
            
            vault.pending_amount += Decimal(amount)
            vault.save()

            # Update teller's balance
            teller.balance -= Decimal(amount)
            teller.save()

            print(f'Successfully deposited {amount} into vault.')
            return transaction
        except Exception as e:
            print(f'Error creating vault transaction: {e}')
    elif transaction_type == 'Withdraw':
        if Decimal(amount) > vault.current_balance:
            messages.error(request, f'Insufficient balance in vault.')
            return None
        
        try:
            transaction = VaultTransaction.objects.create(
                branch = vault.branch,
                transaction_type=transaction_type,
                cash_vault=vault, 
                teller=teller,
                amount=amount,
                )
            
            # update cashvault balance
            vault.current_balance -= Decimal(amount)
            vault.last_updated = datetime.now()
            vault.save()

            # Add teller's pending amount
            teller.pending_amount += Decimal(amount)
            teller.save()

            print(f'Successfully withdrawn {amount} from vault.')
            return transaction
        except Exception as e:
            print(f'Error creating vault transaction: {e}')

def create_teller_to_teller_transaction(request,from_teller, to_teller, amount):
    branch = from_teller.branch
    if Decimal(amount) > from_teller.balance:
        messages.error(request, f'Insufficient balance with {from_teller}.')
        return None  # Ensure the function exits early
    
    # Proceed with transaction creation
    try:
        transaction =TellerToTellerTransaction.objects.create(
            branch = branch,
            from_teller=from_teller, 
            to_teller=to_teller,
            amount=amount,
            )
        # update from_teller balance
        from_teller.balance -= Decimal(amount)
        from_teller.save()

        # Add teller's pending amount
        to_teller.pending_amount += Decimal(amount)
        to_teller.save()
        return transaction
    except Exception as e:
        print(f'Error creating teller to teller transaction: {e}')

def update_vault_transaction(request, transaction_id):
    print(transaction_id)
    vault_transaction = VaultTransaction.objects.get(id=transaction_id)

    try:
        # Update vault balance
        vault = vault_transaction.cash_vault
        vault.current_balance += vault_transaction.amount
        vault.pending_amount -= vault_transaction.amount
        vault.last_updated = datetime.now()
        vault.save()

        vault_transaction.status = "Approved"
        vault_transaction.save()
        messages.success(request, f'Amount of {vault_transaction.amount} is successfully approved for {vault_transaction.cash_vault}')
    except Exception as e:
        # print(f'Error updating vault transaction: {e}')
        messages.error(request, f'Error updating vault transaction: {e}')
        return redirect(reverse('cash_management_view'))

    return redirect(reverse('cash_management_view'))

def update_teller_transaction(request, transaction_id):
    print(transaction_id)
    type = request.GET.get('type')
    if type == 'TellerToTeller':
        try:
            teller_to_teller_transaction = TellerToTellerTransaction.objects.get(id=transaction_id)
            print(teller_to_teller_transaction)

            # Update teller balances
            to_teller = teller_to_teller_transaction.to_teller
            print(to_teller)
            to_teller.balance += teller_to_teller_transaction.amount
            to_teller.pending_amount -= teller_to_teller_transaction.amount
            to_teller.save()

            # Update transaction status
            teller_to_teller_transaction.status = 'Approved'
            teller_to_teller_transaction.save()
            messages.success(request, f'Amount of {teller_to_teller_transaction.amount} is successfully approved for {to_teller}')
        except Exception as e:  
            print(f'Error updating teller to teller transaction: {e}')
    elif type == 'VaultToTeller':
        try:
            vault_transaction = VaultTransaction.objects.get(id=transaction_id)
            print(vault_transaction)

            # Update teller balances
            teller = vault_transaction.teller
            print(teller)
            teller.balance += vault_transaction.amount
            teller.pending_amount -= vault_transaction.amount
            teller.save()

            # Update transaction status
            vault_transaction.status = 'Approved'
            vault_transaction.save()
            messages.success(request, f'Amount of {vault_transaction.amount} is successfully approved for {teller}')
        except Exception as e:
            print(f'Error updating vault transaction: {e}')
    else:
        messages.error(request, 'Error while updating teller transaction, please try again')
        return redirect(reverse('cash_management_view'))

    return redirect(reverse('cash_management_view'))

def cash_management_view(request):
    current_user = request.user
    branch = current_user.employee_detail.branch
    tellers = Teller.objects.all().filter(branch=branch).all()
    vault = CashVault.objects.get(branch=branch)
    
    # Calculate pending amount
    cash_control = 0
    for teller in tellers:
        if teller.pending_amount is not None:
            cash_control += teller.pending_amount
    if vault.pending_amount is not None:
        cash_control += vault.pending_amount

    # Teller Transaction
    teller_transactions = []
    current_teller = Teller.objects.get(employee=current_user)
    teller_teller_transactions = TellerToTellerTransaction.objects.filter(branch=branch, to_teller=current_teller).all()
    teller_vault_transactions = VaultTransaction.objects.filter(branch=branch, transaction_type="Withdraw", teller=current_teller).all()
    # Process TellerToTellerTransactions
    for transaction in teller_teller_transactions:
        teller_transactions.append({
            'transaction_detail': transaction,
            'date': transaction.date,
            'from': transaction.from_teller, 
            'amount': transaction.amount,
            'type': 'TellerToTeller',
        })
    # Process VaultTransactions
    for transaction in teller_vault_transactions:
        teller_transactions.append({
            'transaction_detail': transaction,
            'date': transaction.date,
            'from': transaction.cash_vault,
            'amount': transaction.amount,
            'type': 'VaultToTeller',
        })
    # Sort transactions by date (optional)
    teller_transactions.sort(key=lambda x: x['date'])

    # Vault Transaction
    vault_transactions = VaultTransaction.objects.filter(branch=branch, transaction_type="Deposit").all()
         
    context = {
        'tellers': tellers,
        'vault': vault,
        'current_user': current_user,
        'cash_control': cash_control,
        'teller_transactions': teller_transactions,
        'vault_transactions': vault_transactions,
    }
    
    if request.method == "POST":
        transaction_type = request.POST.get('transaction_type')
        amount = request.POST.get('amount')
        teller_id = request.POST.get('teller-id')
        teller = Teller.objects.get(id=teller_id)
        # print(amount)
        if amount and teller:
            try:
                if transaction_type:
                    v_transaction = create_vault_transaction(request, vault=vault, teller=teller, transaction_type=transaction_type, amount=amount)
                    if v_transaction is None:
                      return redirect(reverse('cash_management_view'))  # Redirect back on failure
                    messages.success(request, f'{transaction_type} of {amount} successfully processed for {teller}.')
                else:
                    from_teller = Teller.objects.get(employee=current_user)
                    to_teller = teller
                    t_transaction = create_teller_to_teller_transaction(request, from_teller=from_teller, to_teller=to_teller, amount=amount)
                    if t_transaction is None:
                        return redirect(reverse('cash_management_view'))  # Redirect back on failure
                    messages.success(request, f'{amount} successfully transferred from {from_teller} to {to_teller}.')
            except Exception as e:
                messages.error(request, f'Error processing transaction: {e}')
        
        return redirect(reverse('cash_management_view'))

    return render(request, 'cash_management/cash_management_view.html', context=context)

