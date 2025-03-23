from django.contrib import admin
from .models import Loan, LoanProcessing, EMIPayment

admin.site.register(Loan)
admin.site.register(LoanProcessing)
admin.site.register(EMIPayment)