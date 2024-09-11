
from django.db import models
from dashboard.models import Member

class SavingsAccount(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.member} - {self.account_number}'

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
