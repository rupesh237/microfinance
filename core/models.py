from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from dashboard.models import Branch

# Create your models here.
class Voucher(models.Model):
    VOUCHER_TYPE_CHOICES = [
        ('Payment', 'Payment'),
        ('Receipt', 'Receipt'),
        ('Journal', 'Journal'),
    ]
    VOUCHER_CATEGORY_CHOICES = [
        ('Cash Sheet', 'Cash Sheet'),
        ('Payment Sheet', 'Payment Sheet'),
        ('Loan', 'Loan'),
        ('Cash and Bank', 'Cash and Bank'),
        ('Manual', 'Manual'),
    ]

    voucher_number = models.CharField(max_length=20, unique=True, db_index=True, blank=True)
    voucher_type = models.CharField(max_length=10, choices=VOUCHER_TYPE_CHOICES)
    category = models.CharField(max_length=30, choices=VOUCHER_CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    description = models.TextField(blank=True)
    transaction_date = models.DateField()
    
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_vouchers")
    created_at = models.DateTimeField(auto_now_add=True)
    # modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="modified_vouchers")
    # modified_at = models.DateTimeField(auto_now=True)

    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True,  related_name="branch_vouchers")

    class Meta:
        ordering = ['-transaction_date', '-created_at']
        verbose_name = "Voucher"
        verbose_name_plural = "Vouchers"

    def __str__(self):
        return f"{self.voucher_type.capitalize()} Voucher #{self.voucher_number}"

    def save(self, *args, **kwargs):
        # Generate voucher_number if it doesn't already exist
        if not self.voucher_number:
            self.voucher_number = self.generate_voucher_number()
        super().save(*args, **kwargs)

    def generate_voucher_number(self):
        # Get today's date and format it (e.g., YYMMDD)
        today_str = timezone.now().strftime('%Y%m%d')

        # Count vouchers created today to generate a sequence number
        count_today = Voucher.objects.filter(transaction_date=timezone.now().date()).count() + 1

        # Create a voucher number with format: YYYYMMDD-SequenceNumber
        return f"{today_str}{count_today:03}"


