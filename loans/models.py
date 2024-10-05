# loans/models.py

from django.db import models
from dashboard.models import Member
from datetime import timedelta

class Loan(models.Model):
    LOAN_TYPE_CHOICES = [
        ('flat', 'Flat Interest'),
        ('declining', 'Declining Balance'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    duration_months = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=100, choices=[('active', 'Active'), ('closed', 'Closed')])

    def __str__(self):
        return f"{self.loan_type} - {self.member.personalInfo.name}"

    def calculate_flat_interest(self):
        # Flat Interest Calculation
        total_interest = (self.amount * self.interest_rate * self.duration_months/12) / 100
        total_repayment = self.amount + total_interest
        return total_repayment / self.duration_months

    def calculate_declining_interest(self):
        # Declining Balance Interest Calculation
        remaining_principal = self.amount
        monthly_interest_rate = self.interest_rate / 12 / 100
        total_repayment = 0
        for month in range(self.duration_months):
            monthly_interest = remaining_principal * monthly_interest_rate
            monthly_principal = self.amount / self.duration_months
            total_repayment += monthly_interest + monthly_principal
            remaining_principal -= monthly_principal
        return total_repayment / self.duration_months

    def calculate_emi_schedule(self):
        # EMI Schedule Calculation (Amortization Schedule)
        emi_schedule = []
        remaining_principal = self.amount
        monthly_interest_rate = self.interest_rate / 12 / 100

        for month in range(self.duration_months):
            # Calculate monthly interest
            monthly_interest = remaining_principal * monthly_interest_rate

            # For flat, the principal remains the same each month
            if self.loan_type == 'flat':
                monthly_principal = self.amount / self.duration_months
            else:
                # For declining, we subtract interest from EMI to get principal
                emi = self.calculate_declining_interest()
                monthly_principal = emi - monthly_interest

            # Calculate total monthly EMI and update remaining principal
            emi_amount = monthly_principal + monthly_interest
            emi_schedule.append({
                'month': month + 1,
                'emi_amount': emi_amount,
                'principal_component': monthly_principal,
                'interest_component': monthly_interest,
                'remaining_principal': remaining_principal - monthly_principal,
            })

            remaining_principal -= monthly_principal

        return emi_schedule
