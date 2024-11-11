from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.template.loader import get_template
from weasyprint import HTML
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.db import transaction

from dashboard.mixins import RoleRequiredMixin

from .models import SavingsAccount, FixedDeposit, RecurringDeposit, CashSheet, PaymentSheet, CURRENT_ACCOUNT_TYPE, Statement
from .forms import SavingsAccountForm, FixedDepositForm, RecurringDepositForm, CashSheetForm, PaymentSheetForm
from dashboard.models import Member

from .filters import StatementFilter

def member_savings(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    account_status = SavingsAccount.ACCOUNT_STATUS
    # Filter based on 'account_status' from request
    account_status_filter = request.GET.get('account_status', '')  # Default to empty string if not provided

    savings_accounts = SavingsAccount.objects.filter(member=member)
    fixed_deposits = FixedDeposit.objects.filter(member=member)
    recurring_deposits = RecurringDeposit.objects.filter(member=member)

    # Apply account_status filter if provided
    if account_status_filter:
        savings_accounts = savings_accounts.filter(status__iexact=account_status_filter)
    
    return render(request, 'savings/member_savings.html', {
        'member': member,
        'account_status': account_status,
        'savings_accounts': savings_accounts,
        'fixed_deposits': fixed_deposits,
        'recurring_deposits': recurring_deposits,
    })

def add_savings_account(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == 'POST':
        form = SavingsAccountForm(request.POST, member=member)

        if form.is_valid():
            savings_account = form.save(commit=False)
            savings_account.member = member 
            # Get the selected account type from the form
            account_type = form.cleaned_data['account_type']

            # Generate account number using member code and account type code
            savings_account.account_number = f"{member.code}.{account_type}.1"
            savings_account.save()
            return redirect('member_savings', member_id=member_id)
    else:
        form = SavingsAccountForm()
    
    return render(request, 'savings/add_savings_account.html', {
        'form': form,
        'member': member
    })

class CashSheetCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = CashSheet
    form_class = CashSheetForm
    template_name = 'transactions/create_cash_sheet.html'
    # success_url = reverse_lazy('member_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(Member, id=member_id)
        kwargs['member'] = member  # Pass member to the form
        return kwargs

    def form_valid(self, form):
        print("Cleaned Data:", form.cleaned_data)  # Debugging line

        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(Member, id=member_id)

        # Get additional fields from the form
        remarks = form.cleaned_data.get('remarks')
        deposited_by = form.cleaned_data.get('deposited_by')
        source_of_fund = form.cleaned_data.get('source_of_fund')

        accounts = SavingsAccount.objects.filter(member=self.kwargs['member_id'])
        for account in accounts:
            amount_field_name = f'amount_{account.id}'
            amount = form.cleaned_data.get(amount_field_name)
            
            if amount is not None and amount > 0:
                print(f"Processing account {account.id} with amount {amount}")
                try:
                    with transaction.atomic():  # Start a database transaction
                        # Create a new CashSheet instance for each account
                        cash_sheet = CashSheet(
                            account=account,
                            member=member,
                            created_by=self.request.user,
                            amount=amount,
                            remarks=remarks,
                            deposited_by=deposited_by,
                            source_of_fund=source_of_fund,
                        )
                        cash_sheet.save()
                        voucher = cash_sheet.create_voucher()

                        # Update account balance
                        prev_balance = account.balance
                        account.balance += amount
                        account.save()

                        # Automatically create a Statement
                        Statement.objects.create(
                            account=account,
                            member=member,
                            cash_sheet=cash_sheet,
                            transaction_type='credit',
                            cr_amount=amount,
                            prev_balance=prev_balance,
                            curr_balance=account.balance,
                            remarks=cash_sheet.remarks,
                            by=cash_sheet.deposited_by,
                            transaction_date=cash_sheet.transaction_date,
                            created_by=self.request.user,
                            voucher=voucher,
                        )
                        print(f"Created CashSheet: {cash_sheet}")
                except Exception as e:
                    print(f"Error creating CashSheet: {e}")

        return HttpResponseRedirect(reverse_lazy('create_cash_sheet', kwargs={'member_id': member_id}))


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member_id = self.kwargs.get('member_id')
        context['member'] = get_object_or_404(Member, id=member_id)  # Pass the member to the context
        return context
    
    def get_success_url(self):
        member_id = self.kwargs.get('member_id')
        # Redirect to a URL that displays the cash sheets for the member
        return reverse_lazy('create_cash_sheet', kwargs={'member_id': member_id})


class PaymentSheetCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = PaymentSheet
    form_class = PaymentSheetForm
    template_name = 'transactions/create_payment_sheet.html'
    # success_url = reverse_lazy('member_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(Member, id=member_id)
        kwargs['member'] = member  # Pass member to the form
        return kwargs

    def form_valid(self, form):
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(Member, id=member_id)

        # Get additional fields from the form
        remarks = form.cleaned_data.get('remarks')
        withdrawn_by = form.cleaned_data.get('withdrawn_by')
        cheque_no = form.cleaned_data.get('cheque_no')


        # Extract only the codes for filtering
        current_account_codes = [code for code, _ in CURRENT_ACCOUNT_TYPE]

        accounts = SavingsAccount.objects.filter(member=self.kwargs['member_id'])
        current_accounts = [account for account in accounts if account.account_type in current_account_codes]
        print(current_accounts)
        for account in current_accounts:
            amount_field_name = f'amount_{account.id}'
            amount = form.cleaned_data.get(amount_field_name)
        
            if amount is not None and amount > 0:
                print(f"Processing account {account.id} with amount {amount}")
                try:
                        payment_sheet = PaymentSheet(
                            account=account,
                            member=member,
                            created_by=self.request.user,
                            amount=amount,
                            remarks=remarks,
                            withdrawn_by=withdrawn_by,
                            cheque_no=cheque_no,
                        )
                        payment_sheet.save()
                        voucher = payment_sheet.create_voucher()
                        print(f"Creating Payment Sheet with account_id: {payment_sheet.account_id}")

                        # Update account balance
                        prev_balance = account.balance
                        account.balance -= amount
                        account.save()

                        # Automatically create a Statement
                        Statement.objects.create(
                            account=account,
                            member=member,
                            payment_sheet=payment_sheet,
                            transaction_type='debit',
                            dr_amount=amount,
                            prev_balance=prev_balance,
                            curr_balance=account.balance,
                            remarks=payment_sheet.remarks,
                            by=payment_sheet.withdrawn_by,
                            transaction_date=payment_sheet.transaction_date,
                            created_by=self.request.user,
                            voucher=voucher,
                        )
                        print(f"Created Payment Sheet: {payment_sheet}")
                except Exception as e:
                    print(f"Error creating Payment Sheet: {e}")

        return HttpResponseRedirect(reverse_lazy('create_payment_sheet', kwargs={'member_id': member_id}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member_id = self.kwargs.get('member_id')
        context['member'] = get_object_or_404(Member, id=member_id)  # Pass the member to the context
        return context
    
    def get_success_url(self):
        member_id = self.kwargs.get('member_id')
        # Redirect to a URL that displays the payment sheets for the member
        return reverse_lazy('create_payment_sheet', kwargs={'member_id': member_id})

@login_required
def statement_list(request, member_id):
     # Filter statements for the specific member
    statements = Statement.objects.filter(member_id=member_id).all()
    # Check if there are any GET parameters (filters applied)
    filters_applied = bool(request.GET)
    
    # Initialize the filter with the queryset and the member_id
    statement_filter = StatementFilter(request.GET, queryset=statements if filters_applied else Statement.objects.none(), member_id=member_id)

    total_credit = statement_filter.qs.get_total_cr_amount()
    total_debit = statement_filter.qs.get_total_dr_amount()
    context = {
               'member_id': member_id,
               'filter': statement_filter,
               'total_credit': total_credit,
               'total_debit': total_debit,
               'net_income': total_credit - total_debit,
               }
    if request.htmx:
        return render(request, 'statement/statement-container.html', context)
    return render(request, 'statement/member_statement_list.html', context)

def statement_pdf_view(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    statements = Statement.objects.filter(member=member)

    # Retrieve filter parameters
    account_type = request.GET.get('account_type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Apply filters if parameters are present
    if account_type:
        statements = statements.filter(account=account_type)
    if start_date:
        statements = statements.filter(transaction_date__gte=start_date)
    if end_date:
        statements = statements.filter(transaction_date__lte=end_date)

    # Calculate totals
    total_credit = sum(statement.cr_amount for statement in statements)
    total_debit = sum(statement.dr_amount for statement in statements)
    total_net = total_credit - total_debit

    # Render the HTML template
    template = get_template('statement/statement-pdf.html')
    html_content = template.render({
        'member': member,
        'statements': statements,
        'total_credit': total_credit,
        'total_debit': total_debit,
        'total_net': total_net,
    })

    # Generate the PDF from the HTML content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="statement_{member_id}.pdf"'
    HTML(string=html_content).write_pdf(response)

    return response


def add_fixed_deposit(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == 'POST':
        form = FixedDepositForm(request.POST)
        if form.is_valid():
            fixed_deposit = form.save(commit=False)
            fixed_deposit.member = member
            fixed_deposit.save()
            return redirect('member_savings', member_id=member_id)
    else:
        form = FixedDepositForm()
    
    return render(request, 'savings/adlistd_fixed_deposit.html', {
        'form': form,
        'member': member
    })

def add_recurring_deposit(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == 'POST':
        form = RecurringDepositForm(request.POST)
        if form.is_valid():
            recurring_deposit = form.save(commit=False)
            recurring_deposit.member = member
            recurring_deposit.save()
            return redirect('member_savings', member_id=member_id)
    else:
        form = RecurringDepositForm()
    
    return render(request, 'savings/add_recurring_deposit.html', {
        'form': form,
        'member': member
    })
