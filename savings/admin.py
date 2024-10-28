from django.contrib import admin
from .models import SavingsAccount, FixedDeposit, RecurringDeposit

admin.site.register(SavingsAccount)
admin.site.register(FixedDeposit)
admin.site.register(RecurringDeposit)
