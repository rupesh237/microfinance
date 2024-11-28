from django.contrib import admin
from .models import Loan, EMIPayment

admin.site.register(Loan)
admin.site.register(EMIPayment)