from django.db import models
from decimal import Decimal

class StatementQuerySet(models.QuerySet):
    def get_receipt(self):
        return self.filter(transaction_type='credit')
    
    def get_payment(self):
        return self.filter(transaction_type='debit')
    
    def get_total_cr_amount(self):
        total = self.get_receipt().aggregate(total=models.Sum('cr_amount'))['total']
        return Decimal(total) if total else Decimal('0.00')
    
    def get_total_dr_amount(self):
        total = self.get_payment().aggregate(total=models.Sum('dr_amount'))['total']
        return Decimal(total) if total else Decimal('0.00')
