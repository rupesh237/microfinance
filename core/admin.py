from django.contrib import admin
from core.models import Voucher, VoucherEntry,CollectionSheet, Teller, CashVault, VaultTransaction, TellerToTellerTransaction, DailyCashSummary

# Register your models here.
admin.site.register(Voucher)
admin.site.register(VoucherEntry)
admin.site.register(CollectionSheet)

admin.site.register(Teller)
admin.site.register(CashVault)
admin.site.register(VaultTransaction)
admin.site.register(TellerToTellerTransaction)
admin.site.register(DailyCashSummary)