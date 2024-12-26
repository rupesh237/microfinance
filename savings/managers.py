from django.db import models
from django.db.models import IntegerField, Value, Case, When
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
    
SAVING_ACCOUNT_TYPE = [
        ('CS', 'Compulsory Saving'),
        ('CF', 'Center Fund'),
        ('OS', 'Optional Saving'),
        ('SBK', 'Samayojan Bachhat Khata'),
        ('CHS', 'Child Saving'),
        ('IS', 'Insurance Saving'),
        ('FS', 'Fixed Saving'),
]

class SavingsAccountQuerySet(models.QuerySet):
     def with_account_type_order(self):
        # Create a mapping for account types with their order
        account_type_order_mapping = {key: index for index, (key, _) in enumerate(SAVING_ACCOUNT_TYPE)}
        
        # Use the mapping to annotate the order
        return self.annotate(
            account_type_order=models.Case(
                *[
                    models.When(account_type=key, then=index)
                    for key, index in account_type_order_mapping.items()
                ],
                default=len(SAVING_ACCOUNT_TYPE),
                output_field=models.IntegerField()
            )
        ).order_by('account_type_order')
     
class SavingsAccountManager(models.Manager):
    def get_queryset(self):
        return SavingsAccountQuerySet(self.model, using=self._db)

    def ordered_by_account_type_display(self):
        return self.get_queryset().with_account_type_order()

