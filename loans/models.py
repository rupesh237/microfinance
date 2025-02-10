# loans/models.py
from django.contrib.auth.models import User
from django.db import models
from dashboard.models import Member
from core.models import Voucher
from decimal import Decimal

LOAN_TYPE_CHOICES = [
        ('Flat', 'Flat Interest'),
        ('Declining', 'Declining Balance'),
        ('Interest_Only', 'Interest Only'),
    ]
class Loan(models.Model):
    LOAN_PURPOSE_CHOICES = [
        ('Crop and Crop Services', 'Crop and Crop Services'),
        ('Wholesale and Retail Business', 'Wholesale and Retail Business'),
        ('Hotel and Restaurants', 'Hotel and Restaurants'),
        ('Fruits and Flowers', 'Fruits and Flowers'),
        ('Animal Husbandary', 'Animal Husbandary'),
        ('Poultry', 'Poultry'),
        ('Other Agricultural and Agro Services', 'Other Agricultural and Agro Services'),
        ('Other Services', 'Other Services'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPE_CHOICES)
    loan_purpose = models.CharField(max_length=50, choices=LOAN_PURPOSE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_demand_date = models.DateField()
    loan_disburse_date = models.DateField()

    status = models.CharField(max_length=100, choices=[( 'applied', 'Applied'), ('analysis', 'Analysis'), ('disburse', 'Disburse'), ('approved', 'Approved'),('active', 'Active'), ('closed', 'Closed')], default='applied')
    is_cleared = models.BooleanField(default=False)

    #Analysis
    loan_analysis_date = models.DateField(null=True, blank=True)
    loan_analysis_amount =  models.DecimalField(default=0.0, max_digits=10, decimal_places=2)
    approved_date = models.DateField(null=True, blank=True)

    # Disburse
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    duration_months = models.IntegerField(default=0, null=True, blank=True)
    payments = models.ManyToManyField('EMIPayment', related_name='loans', blank=True)
    installement_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_by = models.ForeignKey(User, related_name='created_loans', on_delete=models.CASCADE, null=True)
    created_date = models.DateField(null=True, blank=True)


    def __str__(self):
        return f"{self.loan_type} - {self.member.personalInfo.first_name} {self.member.personalInfo.last_name}"

    def calculate_emi(self):
        """
        Calculate EMI only for 'flat' type. Other types are handled in the breakdown.
        """
        if self.loan_type == 'Flat':
            monthly_interest_rate = self.interest_rate / 12 / 100
            emi = (self.amount * monthly_interest_rate * (1 + monthly_interest_rate) ** self.duration_months) / \
                  ((1 + monthly_interest_rate) ** self.duration_months - 1)
            return round(emi, 2)
        return None  # Not applicable for 'declining' or 'interest_only'

    def calculate_emi_breakdown(self):
        """
        Calculate the EMI breakdown based on loan type.
        """
        breakdown = []
        remaining_principal = self.amount

        if self.loan_type == 'Flat':
            emi = self.calculate_emi()
            for month in range(1, self.duration_months + 1):
                monthly_interest = round(remaining_principal * (self.interest_rate / 12 / 100), 2)
                principal_component = round(emi - monthly_interest, 2)

                if month == self.duration_months:
                    principal_component = remaining_principal
                    emi = principal_component + monthly_interest

                remaining_principal = round(remaining_principal - principal_component, 2)
                breakdown.append({
                    'month': month,
                    'emi_amount': emi,
                    'principal_component': principal_component,
                    'interest_component': monthly_interest,
                    'remaining_principal': max(remaining_principal, Decimal('0.00'))
                })
                if remaining_principal <= 0:
                    break

        elif self.loan_type == 'Declining':
            principal_component = round(self.amount / self.duration_months, 2)
            for month in range(1, self.duration_months + 1):
                monthly_interest = round(remaining_principal * (self.interest_rate / 12 / 100), 2)
                
                if month == self.duration_months:
                    # Adjust the final EMI to clear the remaining principal
                    principal_component = remaining_principal
                    emi = principal_component + monthly_interest
                else:
                    emi = round(principal_component + monthly_interest, 2)

                remaining_principal = round(remaining_principal - principal_component, 2)
                breakdown.append({
                    'month': month,
                    'emi_amount': emi,
                    'principal_component': principal_component,
                    'interest_component': monthly_interest,
                    'remaining_principal': max(remaining_principal, Decimal('0.00'))
                })
                if remaining_principal <= 0:
                    break

        elif self.loan_type == 'Interest_Only':
            monthly_interest = round(self.amount * (self.interest_rate / 12 / 100), 2)
            for month in range(1, self.duration_months + 1):
                if month == self.duration_months:
                    # Last month: pay interest + principal
                    emi = round(self.amount + monthly_interest, 2)
                    principal_component = self.amount
                else:
                    emi = monthly_interest
                    principal_component = Decimal('0.00')

                breakdown.append({
                    'month': month,
                    'emi_amount': emi,
                    'principal_component': principal_component,
                    'interest_component': monthly_interest,
                    'remaining_principal': max(self.amount - principal_component, Decimal('0.00'))
                })

        return breakdown
    
    def get_installment_number(self):
        # Count the number of EMIPayment records associated with this loan
        return self.emi_payments.count() + 1


class EMIPayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='emi_payments')
    payment_date = models.DateField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    principal_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    interest_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    voucher = models.ForeignKey(Voucher, on_delete=models.SET_NULL, null=True, blank=True, related_name="emi_payments")

    def __str__(self):
        return f"Payment of {self.amount_paid} for {self.loan}"
    
    @staticmethod
    def get_last_payment(loan):
        return loan.emi_payments.order_by('-payment_date').first()

    @property
    def closing_balance(self):
        """
        Calculate the remaining loan balance after this payment, considering only the principal paid.
        This method ensures that the closing balance for each payment is unique to that payment,
        and reflects the loan balance after that specific payment.
        """
        # Get all previous payments including this payment, ordered by date and ID (or created_at for exact order)
        previous_payments = self.loan.emi_payments.filter(payment_date__lte=self.payment_date).order_by('payment_date', 'id')

        # Sum the principal paid across all previous payments up to and including this one
        total_principal_paid = 0
        for payment in previous_payments:
            # Stop summing once we reach the current payment
            if payment.id == self.id:
                break
            total_principal_paid += payment.principal_paid

        # Add principal paid from this payment
        total_principal_paid += self.principal_paid

        # Calculate the remaining balance by subtracting the total principal paid from the original loan amount
        remaining_balance = self.loan.amount - total_principal_paid

        # Ensure the remaining balance is never negative
        return max(remaining_balance, Decimal('0.00'))


    @property
    def cr(self):
        return self.loan.amount if not self.loan.emi_payments.exists() else 0

    @property
    def dr(self):
        return self.amount_paid