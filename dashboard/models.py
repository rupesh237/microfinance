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

GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ]
MARITAL_STATUS_CHOICES = [
    ('Single', 'Single'),
    ('Married', 'Married'),
    ('Divorced', 'Divorced'),
    ('Widow', 'Widow'),
]
FAMILY_STATUS_CHOICES = [
    ('Poor', 'Poor'),
    ('Medium', 'Medium'),
    ('High', 'High'),
    ('Rich', 'Rich'),
]
EDUCATION_CHOICES = [
    ('Illiterate', 'Illiterate'),
    ('Literate', 'Literate'),
    ('Under SLC', 'High'),
    ('SLC', 'SLC'),
    ('Intermediate', 'Intermediate'),
    ('Bachelor', 'Bachelor'),
    ("Master's Degree", "Master's Degree"),
    ("Ph.D.", "Ph.D."),
]
RELIGION_CHOICES = [
    ('Hinduism', 'Hinduism'),
    ('Buddhism', 'Buddhism'),
    ('Kirat', 'Kirat'),
    ('Christainity', 'Christainity'),
    ('Islam', 'Islam'),
    ('Jainism', 'Jainism'),
    ('Bon', 'Bon'),
]
OCCUPATION_CHOICES = [
    ('Agriculture', 'Agriculture'),
    ('Business', 'Business'),
    ('Housewife', 'Housewife'),
    ('Foreign Employment', 'Foreign Employment'),
]

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

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
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
        ('GENERAL', 'General'),
        ('PUBLIC', 'Public'),
        ('BUSINESS', 'Business'),
        ('OTHERS', 'Others'), 
    ]

    MEETING_REPEAT_TYPE_CHOICES = [
        ('fixed interval', 'Fixed Interval'),
        ('fixed date', 'Fixed Date'),
    ]

    class MeetingInterval(models.IntegerChoices):
        TWO_WEEKS = 14, '14 days'
        FOUR_WEEKS = 28, '28 days'

    status = models.CharField(max_length=25, default="Active")

    code = models.CharField(max_length=20, null=True)
    input_code = models.CharField(max_length=20, null=True)
    name = models.CharField(max_length=100)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name="centerprovince", null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="centerdistrict", null=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name="centermunicipality", null=True)

    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='general')

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

    status = models.CharField(max_length=50, default='Active')

    def __str__(self):
        return self.name
    
class Member(models.Model):
    MEMBER_CATEGORY_CHOICES = [
        ('Group Member', 'Group Member'),
        ('Public Member', 'Public Member'),
    ]

    MEMBER_STATUS = [
        ('A', 'Active'),
        ('IA', 'In-Active'),
        ('RTR', 'Ready To Register'),
        ('D', 'Dropout'),
        ('p', 'Public'),
        ('D', 'Death'), 
    ]

    member_category = models.CharField(max_length=20, choices=MEMBER_CATEGORY_CHOICES, default="General Member")
    center = models.ForeignKey(Center, on_delete=models.CASCADE, null=True)
    group = models.ForeignKey(GRoup, on_delete=models.CASCADE)
    member_code = models.IntegerField(null=True)
    code = models.CharField(max_length=20, null=True)
    position = models.IntegerField(null=True)

    status = models.CharField(max_length=25, choices=MEMBER_STATUS, default='RTR')
    def __str__(self):
        return f'Member {self.id} in group {self.group.name}'

# Member information from here on:
class AddressInformation(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='addressInfo')
    # permanent address
    permanent_province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name="member_permanent_province", null=True)
    permanent_district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="member_permanent_district", null=True)
    permanent_municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name="member_permanent_municipality", null=True)
    permanent_ward_no = models.IntegerField(default=1)
    permanent_tole = models.CharField(max_length=50)
    permanent_house_no = models.CharField(max_length=50, blank=True, null=True)

    # current address
    current_province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name="member_current_province", null=True)
    current_district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="member_current_district", null=True)
    current_municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name="member_current_municipality", null=True)
    current_ward_no = models.IntegerField(default=1)
    current_tole = models.CharField(max_length=50)
    current_house_no = models.CharField(max_length=50, blank=True, null=True)

    # old address
    old_province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name="member_old_province", null=True)
    old_district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="member_old_district", null=True)
    old_municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name="member_old_municipality", null=True)
    old_ward_no = models.IntegerField(default=1)
    old_tole = models.CharField(max_length=50)
    old_house_no = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.member}"

class PersonalInformation(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='personalInfo')
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, null=True)
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES, default='Female')
    marital_status = models.CharField(max_length=30, choices=MARITAL_STATUS_CHOICES)
    family_status = models.CharField(max_length=20, choices=FAMILY_STATUS_CHOICES)
    education = models.CharField(max_length=30, choices=EDUCATION_CHOICES)
    religion = models.CharField(max_length=30, choices=RELIGION_CHOICES)
    occupation = models.CharField(max_length=30, choices=OCCUPATION_CHOICES)
    family_member_no = models.IntegerField()
    date_of_birth = models.DateField()

    voter_id = models.CharField(max_length=20, blank=True, null=True)
    voter_id_issued_on = models.DateField(blank=True, null=True)

    citizenship_no = models.CharField(max_length=20)
    issued_from = models.CharField(max_length=20)
    issued_date = models.DateField()

    marriage_reg_no = models.CharField(max_length=20, blank=True, null=True)
    registered_vdc = models.CharField(max_length=20, blank=True, null=True)
    marriage_regd_date = models.DateField(blank=True, null=True)

    registered_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    registered_date = models.DateField(auto_now_add=True)

    file_no = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

RELATIONSHIP_CHOICES = [
    ('Father', 'Father'),
    ('Husband', 'Husband'),
    ('Father-In-Law', 'Father-In-Law'),
    ('Son', 'Son'),
    ('Daughter', 'Daughter'),
]
class FamilyInformation(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='familyInfo')

    family_member_name = models.CharField(max_length=50)
    relationship = models.CharField(max_length=30, choices=RELATIONSHIP_CHOICES)
    date_of_birth = models.DateField()
    citizenship_no = models.CharField(max_length=20, blank=True, null=True)
    issued_from = models.CharField(max_length=20, blank=True, null=True)
    issued_date = models.DateField(blank=True, null=True)

    education = models.CharField(max_length=30, choices=EDUCATION_CHOICES, null=True, blank=True)
    occupation = models.CharField(max_length=30, blank=True, null=True)
    monthly_income = models.FloatField(default=0.00, blank=True, null=True)
    phone_number = models.CharField(max_length=15)

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
    agriculture_income = models.FloatField(default=0.0)
    animal_farming_income = models.FloatField(default=0.0)
    business_income = models.FloatField(default=0.0)
    abroad_employment_income = models.FloatField(default=0.0)
    wages_income = models.FloatField(default=0.0)
    personal_job_income = models.FloatField(default=0.0)
    government_post = models.FloatField(default=0.0)
    pension = models.FloatField(default=0.0)
    other = models.FloatField(default=0.0)
    

class ExpensesInformation(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='expensesInfo')
    house_expenses = models.FloatField(default=0.0)
    education_expenses = models.FloatField(default=0.0)
    health_expenses = models.FloatField(default=0.0)
    festival_expenses = models.FloatField(default=0.0)
    clothes_expenses = models.FloatField(default=0.0)
    communication_expenses = models.FloatField(default=0.0)
    fuel_expenses = models.FloatField(default=0.0)
    entertaiment_expenses = models.FloatField(default=0.0)
    other_expenses = models.FloatField(default=0.0)