from django.db import models, transaction
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

from dashboard.models import Branch, Center, Member

# Create your models here.
class CashManagement(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Cash Management - {self.branch}"

class Voucher(models.Model):
    VOUCHER_TYPE_CHOICES = [
        ('Payment', 'Payment'),
        ('Receipt', 'Receipt'),
        ('Journal', 'Journal'),
    ]
    VOUCHER_CATEGORY_CHOICES = [
        ('Cash Sheet', 'Cash Sheet'),
        ('Payment Sheet', 'Payment Sheet'),
        ('Collection Sheet', 'Collection Sheet'),
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
        today_str = timezone.now().strftime('%Y%m%d')
        last_voucher = Voucher.objects.filter(transaction_date=timezone.now().date()).order_by('voucher_number').last()
        if last_voucher:
            last_sequence = int(last_voucher.voucher_number[-3:])
            next_sequence = last_sequence + 1
        else:
            next_sequence = 1
        return f"{today_str}{next_sequence:03}"
    

class CollectionSheet(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="collection_sheets")
    center = models.ForeignKey(Center, on_delete=models.CASCADE, related_name="collection_sheets")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="collection_sheets")
    member_collection = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    special_record = models.CharField(max_length=100, choices=[( 'A', 'A'), ('P', 'P'), ('L', 'L'), ('S', 'S'),('D', 'D'), ('B', 'B'), ('M', 'M'),('E', 'E')], default='P', null=True, blank=True)

    meeting_no = models.IntegerField(default=1)
    meeting_date = models.DateField()

    evaluation_no = models.IntegerField()
    meeting_by = models.ForeignKey(User, on_delete=models.CASCADE)
    supervision_by_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collection_sheet_supervisor_1")
    supervision_by_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collection_sheet_supervisor_2", null=True, blank=True)
    next_meeting_date = models.DateField()

    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    status = models.CharField(max_length=100, choices=[( 'Saved', 'Saved'), ('Submitted', 'Submitted'), ('Approved', 'Approved'), ('Accepted', 'Accepted'),('Cancelled', 'Cancelled')], default='Saved')

    def save(self, *args, **kwargs):
        # Dynamically set the meeting number and date based on existing meetings for this center
        if not self.meeting_date:
            self.meeting_date = self.calculate_meeting_date()

        if not self.meeting_no:
            self.meeting_no = self.calculate_meeting_no()

        super().save(*args, **kwargs)

    def calculate_meeting_no(self):
        """
        Calculate the meeting number for this center based on existing meetings.
        The meeting_no will be based on the number of meetings that have already occurred for the center.
        """
        # Get the meetings for the current center that are already scheduled
        meetings = CollectionSheet.objects.filter(center=self.center).order_by('meeting_date')
        
        # Get the number of meetings already scheduled for this center
        meeting_count = meetings.count()

        # The next meeting number will be the next in the sequence
        return meeting_count + 1

    def calculate_meeting_date(self):
        """
        Calculate the meeting date based on the center's schedule.
        For simplicity, this example assumes meetings are spaced out by a fixed interval, like 30 days.
        """
        # Get the last meeting's date, or use the first day of the current month if no meetings exist
        last_meeting = CollectionSheet.objects.filter(center=self.center).order_by('-meeting_date').first()

        if last_meeting:
            # For this example, meetings occur every 30 days
            next_meeting_date = last_meeting.meeting_date + timedelta(days=30)
        else:
            # If no meeting exists, set the first meeting to the 1st day of the current month
            next_meeting_date = timezone.datetime(timezone.now().year, timezone.now().month, 1)

        return next_meeting_date

    
    def __str__(self):
        return f"CollectionSheet {self.id} for Member {self.member} on {self.meeting_date}"


