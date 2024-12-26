
from django.db import models
from django.contrib.auth.models import User
from dashboard.models import Member, Branch

from core.models import Voucher

from savings.managers import StatementQuerySet, SavingsAccountManager

from django.utils import timezone

INITIAL_SAVING_ACCOUNT_TYPE = [
        ('CS', 'Compulsory Saving'),
        ('CF', 'Center Fund'),
        ('OS', 'Optional Saving'),
        ('SBK', 'Samayojan Bachhat Khata'),
]

SAVING_ACCOUNT_TYPE = [
        ('CS', 'Compulsory Saving'),
        ('CF', 'Center Fund'),
        ('OS', 'Optional Saving'),
        ('SBK', 'Samayojan Bachhat Khata'),
        ('CHS', 'Child Saving'),
        ('IS', 'Insurance Saving'),
        ('FS', 'Fixed Saving'),
]

CURRENT_ACCOUNT_TYPE = [
        ('OS', 'Optional Saving'),
        ('SBK', 'Samayojan Bachhat Khata'),
]


class SavingsAccount(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="SavingsAccount")
    account_type = models.CharField(max_length=50, choices=SAVING_ACCOUNT_TYPE, default='CS')
    account_number = models.CharField(max_length=20, unique=True)
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2, default=5.00)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_on = models.DateTimeField(auto_now_add=True)

    ACCOUNT_STATUS = [
        ('A', 'Active'),
        ('IA', 'In-Active'),
    ]

    status = models.CharField(max_length=25, choices=ACCOUNT_STATUS, default='A')

    objects = SavingsAccountManager()
    

    def __str__(self):
        return f'{self.account_type_display} - {self.account_number}'

    @property
    def account_type_display(self):
        return self.get_account_type_display()


class FixedDeposit(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='fixed_deposits')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    maturity_date = models.DateField()

    def __str__(self):
        return f"FD - {self.amount} by {self.member.personalInfo.name}"

class RecurringDeposit(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='recurring_deposits')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Duration in months")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"RD - {self.amount} by {self.member.personalInfo.name}"


class CashSheet(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="cashsheet")
    account = models.ForeignKey(SavingsAccount, on_delete=models.CASCADE, related_name='cashsheet_account')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    deposited_by = models.CharField(max_length=30, null=True, blank=True)
    remarks = models.CharField(max_length=100, null=True, blank=True)
    source_of_fund = models.CharField(max_length=50, null=True, blank=True)

    transaction_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def create_voucher(self):
        voucher = Voucher.objects.create(
            voucher_type='Receipt',
            category='Cash Sheet',
            amount=self.amount,
            description=f'Receipt of {self.account.account_number} {self.account.account_type}',
            transaction_date=self.transaction_date,
            created_by=self.created_by,
        )
        return voucher

    def __str__(self):
        return f"{self.member.code}: Cash Sheet for {self.account}"
    
class PaymentSheet(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="paymentsheet")
    account = models.ForeignKey(SavingsAccount, on_delete=models.CASCADE, related_name='payment_account')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    withdrawn_by = models.CharField(max_length=30, null=True, blank=True)
    remarks = models.CharField(max_length=100, null=True, blank=True)
    cheque_no = models.CharField(max_length=50, null=True, blank=True)

    transaction_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def create_voucher(self):
        voucher = Voucher.objects.create(
            voucher_type='Payment',
            category='Payment Sheet',
            amount=self.amount,
            description=f'Approved by {self.created_by}',
            transaction_date=self.transaction_date,
            created_by=self.created_by,
        )
        return voucher

    def __str__(self):
        return f"{self.member.code}: Payment Sheet for {self.account}"
    
class Statement(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]

    SAVINGS_CATEGORY_CHOICES = [
        ('Cash Sheet', 'Cash Sheet'),
        ('Payment Sheet', 'Payment Sheet'),
        ('Loan', 'Loan'),
        ('Charge', 'Charge'),
        ('Collection', 'Collection'),
    ]

    account = models.ForeignKey(SavingsAccount, on_delete=models.CASCADE, related_name='account_stat')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="member_stat")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=50, choices=SAVINGS_CATEGORY_CHOICES)
    cr_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    dr_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    prev_balance = models.DecimalField(max_digits=12, decimal_places=2)
    curr_balance = models.DecimalField(max_digits=12, decimal_places=2)
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    by = models.CharField(max_length=50, null=True, blank=True)
    transaction_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    cash_sheet = models.ForeignKey(CashSheet, on_delete=models.CASCADE, related_name='statement_cashsheet', blank=True, null=True)
    payment_sheet = models.ForeignKey(PaymentSheet, on_delete=models.CASCADE, related_name='statement_paymentsheet', blank=True, null=True)

    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='voucher_statement')

    objects = StatementQuerySet.as_manager()


    def __str__(self):
        return f"{self.account} - {self.transaction_type}"

