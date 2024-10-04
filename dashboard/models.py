from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Create your models here.
# class Nepal(models.MOdel):
#     name = 'Nepal'
class Province(models.TextChoices):
    PROVINCE_1 = 'Province No. 1', _('Province No. 1')
    PROVINCE_2 = 'Madhesh Province', _('Madhesh Province')
    BAGMATI = 'Bagmati Province', _('Bagmati Province')
    GANDAKI = 'Gandaki Province', _('Gandaki Province')
    LUMBINI = 'Lumbini Province', _('Lumbini Province')
    KARNALI = 'Karnali Province', _('Karnali Province')
    SUDURPASCHIM = 'Sudurpashchim Province', _('Sudurpashchim Province')

class GenderTypes(models.TextChoices):
    MALE = 'M', _('Male')
    FEMALE = 'F', _('Female')


class UserRoles(models.TextChoices):
    BRANCH_MANAGER = 'BranchManager', _('Branch Manager')
    LOAN_OFFICER = 'LoanOfficer', _('Loan Officer')
    CASHIER = 'Cashier', _('Cashier')


class ClientRoles(models.TextChoices):
    FIRST_LEADER = 'FirstLeader', _('First Leader')
    SECOND_LEADER = 'SecondLeader', _('Second Leader')
    GROUP_MEMBER = 'GroupMember', _('Group Member')


class AccountStatus(models.TextChoices):
    APPLIED = 'Applied', _('Applied')
    WITHDRAWN = 'Withdrawn', _('Withdrawn')
    APPROVED = 'Approved', _('Approved')
    REJECTED = 'Rejected', _('Rejected')
    CLOSED = 'Closed', _('Closed')


class InterestTypes(models.TextChoices):
    FLAT  = 'Flat', _('Flat')
    DECLINING = 'Declining', _('Declining')


class ReceiptTypes(models.TextChoices):
    ENTRANCE_FEE = 'EntranceFee', _('Entrance Fee')
    MEMBERSHIP_FEE = 'MembershipFee', _('Membership Fee')
    BOOK_FEE = 'BookFee', _('Book Fee')
    LOAN_PROCESSING_FEE = 'LoanProcessingFee', _('Loan Processing Fee')
    SAVINGS_DEPOSIT = 'SavingsDeposit', _('Savings Deposit')
    FIXED_DEPOSIT = 'FixedDeposit', _('Fixed Deposit')
    RECURRING_DEPOSIT = 'RecurringDeposit', _('Recurring Deposit')
    ADDITIONAL_SAVINGS = 'AdditionalSavings', _('Additional Savings')
    SHARE_CAPITAL = 'ShareCapital', _('Share Capital')
    PENAL_INTEREST = 'PenalInterest', _('Penal Interest')
    LOAN_DEPOSIT = 'LoanDeposit', _('Loan Deposit')
    INSURANCE = 'Insurance', _('Insurance')


class FdRdStatus(models.TextChoices):
    OPENED = 'Opened', _('Opened')
    PAID = 'Paid', _('Paid')
    CLOSED = 'Closed', _('Closed')


class PaymentTypes(models.TextChoices):
    LOANS = 'Loans', _('Loans')
    TRAVELLING_ALLOWANCE = 'TravellingAllowance', _('Travelling Allowance')
    PAYMENT_OF_SALARY = 'PaymentOfSalary', _('Payment of Salary')
    PRINTING_CHARGES = 'PrintingCharges', _('Printing Charges')
    STATIONARY_CHARGES = 'StationaryCharges', _('Stationary Charges')
    OTHER_CHARGES = 'OtherCharges', _('Other Charges')
    SAVINGS_WITHDRAWAL = 'SavingsWithdrawal', _('Savings Withdrawal')
    FIXED_WITHDRAWAL = 'FixedWithdrawal', _('Fixed Deposit Withdrawal')
    RECURRING_WITHDRAWAL = 'RecurringWithdrawal', _('Recurring Deposit Withdrawal')


class Province(models.Model):
    name = models.CharField(max_length=64, unique=True)
    # country = models.ForeignKey(Nepal, on_delete=models.CASCADE, related_name="zone" )

    def __str__(self):
        return f'{self.name}'
    
class District(models.Model):
    name = models.CharField(max_length=64)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name="districts")

    def __str__(self):
        return f'{self.name}'
    
class Municipality(models.Model):
    name = models.CharField(max_length=64)
    
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="municipalities")

    def __str__(self):
        return f'{self.name}'
    
class Branch(models.Model):
    code = models.CharField(max_length=3)
    # is_created_on = models.DateTimeField(default=now)
    #is_created_by = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name="branches")
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="branches")
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name="branches")
    tole = models.CharField(max_length=64, null=True, blank=True)
    wardNo = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.name} ({self.municipality})'

class Employee(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    image = models.ImageField(upload_to= settings.PHOTO_PATH, blank=True, null=True)
    citizenship_card = models.ImageField(upload_to=settings.PHOTO_PATH, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} ({self.role})'
    

# center infromation
class Center(models.Model):

    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('public', 'Public'),
        ('business', 'Business'),
        ('others', 'Others'), 
    ]

    MEETING_REPEAT_TYPE_CHOICES = [
        ('fixed interval', 'Fixed Interval'),
        ('fixed date', 'Fixed Date'),
    ]

    class MeetingInterval(models.IntegerChoices):
        TWO_WEEKS = 14, '14 days'
        FOUR_WEEKS = 28, '28 days'

    code = models.CharField(max_length=20, null=True)
    input_code = models.CharField(max_length=20, null=True)
    name = models.CharField(max_length=100)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name="centerprovince", null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="centerdistrict", null=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name="centermunicipality", null=True)

    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES,null=True)

    no_of_group = models.IntegerField( default=1, null=True)
    no_of_members = models.IntegerField( default=4, null=True)
    meeting_place = models.CharField(max_length=50, null=True)
    meeting_distance = models.IntegerField(default=0, null=True)
    formed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="formed_by", null=True)
    formed_date = models.DateTimeField(auto_now_add=True)

    meeting_start_date = models.DateTimeField(null=True)
    meeting_start_time = models.TimeField(null=True)
    meeting_end_time = models.TimeField(null=True)
    walking_time = models.TimeField(null=True)
    meeting_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="meeting_by") #optional

    meeting_repeat_type = models.CharField(max_length=25, choices=MEETING_REPEAT_TYPE_CHOICES, null=True)
    meeting_interval = models.IntegerField(choices=MeetingInterval.choices, default=MeetingInterval.TWO_WEEKS, null=True)
    meeting_date = models.IntegerField(default=1,null=True)
    every = models.IntegerField(default=1, null=True)


    #CENTER ESTD
    pgt_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pgt_by", null=True)
    from_date = models.DateTimeField(null=True)
    to_date = models.DateTimeField(null=True)
    grt_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="grt_by", null=True)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="app_by", null=True)


    def __str__(self):
        return self.code

# Group information
class GRoup(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    center = models.ForeignKey(Center, on_delete=models.CASCADE)
    position = models.IntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Member(models.Model):
    center = models.ForeignKey(Center, on_delete=models.CASCADE, null=True)
    group = models.ForeignKey(GRoup, on_delete=models.CASCADE)
    member_code = models.IntegerField(null=True)
    code = models.CharField(max_length=20, null=True)
    def __str__(self):
        return f'Member {self.id} in group {self.group.name}'

# Member information from here on:
class PersonalInformation(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='personalInfo')
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    current_address = models.TextField()
    permanent_address = models.TextField()

    def __str__(self):
        return self.name

class FamilyInformation(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='familyInfo')
    sons = models.IntegerField(default=0)
    daughters = models.IntegerField(default=0)
    husband = models.CharField(max_length=100, blank=True, null=True)
    father = models.CharField(max_length=100, blank=True, null=True)

class LivestockInformation(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='livestockInfo')
    cows = models.IntegerField(default=0)
    buffalo = models.IntegerField(default=0)
    goat = models.IntegerField(default=0)
    sheep = models.IntegerField(default=0)

class HouseInformation(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='houseInfo')
    concrete = models.BooleanField(default=False)
    mud = models.BooleanField(default=False)
    iron = models.BooleanField(default=False)

class LandInformation(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='landInfo')
    farming_land = models.FloatField(default=0.0)
    other_land = models.FloatField(default=0.0)

class IncomeInformation(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='incomeInfo')
    earning = models.FloatField(default=0.0)
    farming_income = models.FloatField(default=0.0)
    cattle_income = models.FloatField(default=0.0)

class ExpensesInformation(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='expensesInfo')
    house_rent = models.FloatField(default=0.0)
    food_expense = models.FloatField(default=0.0)
    health_expense = models.FloatField(default=0.0)
    other_expenses = models.FloatField(default=0.0)