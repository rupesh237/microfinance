# loans/models.py

from django.db import models
from dashboard.models import Member
from decimal import Decimal

class Loan(models.Model):
    LOAN_TYPE_CHOICES = [
        ('flat', 'Flat Interest'),
        ('declining', 'Declining Balance'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payments = models.ManyToManyField('EMIPayment', related_name='loans', blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    duration_months = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=100, choices=[('active', 'Active'), ('closed', 'Closed')])

    def __str__(self):
        return f"{self.loan_type} - {self.member.personalInfo.name}"

    def calculate_emi(self):
        """
        Calculate the EMI using the standard formula:
        EMI = [P * r * (1 + r)^n] / [(1 + r)^n – 1]
        """
        monthly_interest_rate = self.interest_rate / 12 / 100
        emi = (self.amount * monthly_interest_rate * (1 + monthly_interest_rate) ** self.duration_months) / \
              ((1 + monthly_interest_rate) ** self.duration_months - 1)
        return round(emi, 2)

    def calculate_emi_breakdown(self):
        """
        Calculate the detailed EMI breakdown for each month.
        Return a list of dictionaries with EMI components for each month.
        """
        emi = self.calculate_emi()
        breakdown = []
        remaining_principal = self.amount

        for month in range(1, self.duration_months + 1):
            monthly_interest = round(remaining_principal * (self.interest_rate / 12 / 100), 2)
            principal_component = round(emi - monthly_interest, 2)
            remaining_principal = round(remaining_principal - principal_component, 2)

            breakdown.append({
                'month': month,
                'emi_amount': emi,
                'principal_component': principal_component,
                'interest_component': monthly_interest,
                'remaining_principal': max(remaining_principal, Decimal('0.00'))  # To ensure remaining principal is not negative
            })

        return breakdown
    

class EMIPayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='emi_payments')
    payment_date = models.DateField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Payment of {self.amount_paid} for {self.loan}"

    @property
    def closing_balance(self):
        total_paid = sum(payment.amount_paid for payment in self.loan.emi_payments.all())
        return self.loan.amount - total_paid
