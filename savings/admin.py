from django.contrib import admin
from .models import SavingsAccount, FixedDeposit, RecurringDeposit, CashSheet, PaymentSheet, Statement

admin.site.register(SavingsAccount)
admin.site.register(FixedDeposit)
admin.site.register(RecurringDeposit)
admin.site.register(CashSheet)
admin.site.register(PaymentSheet)
admin.site.register(Statement)