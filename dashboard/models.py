from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from nepali_datetime_field.models import NepaliDateField

# Create your models here.
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
    INTEREST_ONLY = 'Interest Only', _('Interest Only')


class FdRdStatus(models.TextChoices):
    OPENED = 'Opened', _('Opened')
    PAID = 'Paid', _('Paid')
    CLOSED = 'Closed', _('Closed')



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
    ('Engineer', 'Engineer'),
    ('Teacher', 'Teacher'),
    ('Student', 'Student'),
    ('Doctor', 'Doctor'),
    ('Business', 'Business'),
    ('Housewife', 'Housewife'),
    ('Government Job', 'Government Job'),
    ('Private Job', 'Private Job'),
    ('Retired', 'Retired'),
    ('Foreign Employment', 'Foreign Employment'),
    ('Other', 'Other'),
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
        return f'{self.code}: {self.name}'

class Employee(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_detail')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    image = models.ImageField(upload_to= settings.PHOTO_PATH, blank=True, null=True)
    citizenship_card = models.ImageField(upload_to=settings.PHOTO_PATH, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="employees")

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
    no_of_members = models.IntegerField( default=5, null=True)
    meeting_place = models.CharField(max_length=50, null=True)
    meeting_distance = models.IntegerField(default=0, null=True)
    formed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="formed_by", null=True)
    formed_date = models.DateTimeField(auto_now_add=True)

    meeting_start_date = models.DateTimeField(null=True)
    meeting_start_time = models.TimeField(null=True)
    meeting_end_time = models.TimeField(null=True)
    walking_time = models.CharField(max_length=20, null=True)
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
    
    class Meta:
        ordering = ['formed_date']  

# Group information
class GRoup(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    center = models.ForeignKey(Center, on_delete=models.CASCADE, related_name="groups")
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
    registered_date = models.DateField(null=True, blank=True)
    dropout_date = models.DateField(null=True, blank=True)

    temporary = models.BooleanField(default=True)
    def __str__(self):
        return f'Member {self.id} in group {self.group.name}'

# Member documents:
DOC_TYPE_CHOICES = [
    ('Citizenship', 'Citizenship'),
    ('Passport', 'Passport'),
    ('Voter ID', 'Voter ID'),
    ('Driver License', 'Driver License'),
]

class PersonalMemberDocument(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="personal_documents")
    document_type = models.CharField(max_length=50, choices=DOC_TYPE_CHOICES)
    document_file = models.FileField(upload_to='member/personal/', blank=True, null=True)
    uploaded_date = models.DateField(auto_now=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_member_documents', null=True)

    def __str__(self):
        return f"{self.member.personalInfo.first_name} {self.member.personalInfo.middle_name} {self.member.personalInfo.last_name} - Personal Document"

class FamilyMemberDocument(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="family_documents")
    relationship = models.CharField(max_length=100)  # Example: Father, Mother, Spouse
    document = models.FileField(upload_to='member/family/', blank=True, null=True)
    uploaded_date = models.DateField(null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_family_documents', null=True)

    def __str__(self):
        return f"{self.member.personalInfo.first_name} {self.member.personalInfo.middle_name} {self.member.personalInfo.last_name} - {self.relationship} Document"
    
# Member information from here on:
class AddressInformation(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ('current', 'Current Address'),
        ('permanent', 'Permanent Address'),
        ('old', 'Old Address'),
    ]
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='address_info')  # Changed to ForeignKey
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name="member_permanent_province", null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="member_permanent_district", null=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name="member_permanent_municipality", null=True)
    ward_no = models.IntegerField(default=1)
    tole = models.CharField(max_length=50)
    house_no = models.CharField(max_length=50, blank=True, null=True)
    address_type = models.CharField(choices=ADDRESS_TYPE_CHOICES, max_length=20)

    def __str__(self):
        return f"{self.member.personalInfo.first_name} {self.member.personalInfo.middle_name} {self.member.personalInfo.last_name} - {self.address_type}"

    class Meta:
        verbose_name = 'Address Information'
        verbose_name_plural = 'Address Information'

class PersonalInformation(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='personalInfo')
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='member/personal/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, null=True)
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES, default='Female')
    marital_status = models.CharField(max_length=30, choices=MARITAL_STATUS_CHOICES)
    family_status = models.CharField(max_length=20, choices=FAMILY_STATUS_CHOICES)
    education = models.CharField(max_length=30, choices=EDUCATION_CHOICES)
    religion = models.CharField(max_length=30, choices=RELIGION_CHOICES)
    occupation = models.CharField(max_length=30, choices=OCCUPATION_CHOICES)
    family_member_no = models.IntegerField()
    date_of_birth = NepaliDateField()

    voter_id = models.CharField(max_length=20, blank=True, null=True)
    voter_id_issued_on = NepaliDateField(blank=True, null=True)

    citizenship_no = models.CharField(max_length=20)
    issued_from = models.CharField(max_length=20)
    issued_date = NepaliDateField(blank=False,)

    marriage_reg_no = models.CharField(max_length=20, blank=True, null=True)
    registered_vdc = models.CharField(max_length=20, blank=True, null=True)
    marriage_regd_date = NepaliDateField(blank=True, null=True)

    registered_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    registered_date = NepaliDateField(blank=True, null=True)

    file_no = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

RELATIONSHIP_CHOICES = [
    ('Father', 'Father'),
    ('Husband', 'Husband'),
    ('Father-In-Law', 'Father-In-Law'),
    ('Wife', 'Wife'),
    ('Son', 'Son'),
    ('Daughter', 'Daughter'),
    ('Mother', 'Mother'),
    ('Mother-In-Law', 'Mother-In-Law'),
    ('Brother', 'Brother'),
    ('Sister', 'Sister'),
    ('Grandfather', 'Grandfather'),
    ('Grandmother', 'Grandmother'),
    ('Uncle', 'Uncle'),
    ('Aunt', 'Aunt'),
    ('Grandson', 'Grandson'),
    ('Granddaughter', 'Granddaughter'),
    ('Nephew', 'Nephew'),
    ('Niece', 'Niece'),
    ('Cousin', 'Cousin'),
    ('Other', 'Other'),
]
class FamilyInformation(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='familyInfo')

    family_member_name = models.CharField(max_length=50)
    relationship = models.CharField(max_length=30, choices=RELATIONSHIP_CHOICES)
    date_of_birth = NepaliDateField()
    citizenship_no = models.CharField(max_length=20, blank=True, null=True)
    issued_from = models.CharField(max_length=20, blank=True, null=True)
    issued_date = NepaliDateField(blank=True, null=True)

    education = models.CharField(max_length=30, choices=EDUCATION_CHOICES, null=True, blank=True)
    occupation = models.CharField(max_length=30, blank=True, null=True)
    monthly_income = models.FloatField(default=0.00, blank=True, null=True)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.member.personalInfo.first_name}'s {self.relationship}: {self.family_member_name}"

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
    # animal_farming_land = models.FloatField(default=0.0)
    # business_land = models.FloatField(default=0.0) 
    other_land = models.FloatField(default=0.0)

class IncomeInformation(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='incomeInfo')
    agriculture_income = models.FloatField(default=0.0, null=True, blank=True)
    animal_farming_income = models.FloatField(default=0.0, null=True, blank=True)
    business_income = models.FloatField(default=0.0, null=True, blank=True)
    abroad_employment_income = models.FloatField(default=0.0, null=True, blank=True)
    wages_income = models.FloatField(default=0.0, null=True, blank=True)
    personal_job_income = models.FloatField(default=0.0, null=True, blank=True)
    government_post = models.FloatField(default=0.0, null=True, blank=True)
    pension = models.FloatField(default=0.0, null=True, blank=True)
    other = models.FloatField(default=0.0, null=True, blank=True)
    

class ExpensesInformation(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='expensesInfo')
    house_expenses = models.FloatField(default=0.0, null=True, blank=True)
    education_expenses = models.FloatField(default=0.0, null=True, blank=True)
    health_expenses = models.FloatField(default=0.0, null=True, blank=True)
    festival_expenses = models.FloatField(default=0.0, null=True, blank=True)
    clothes_expenses = models.FloatField(default=0.0, null=True, blank=True)
    communication_expenses = models.FloatField(default=0.0, null=True, blank=True)
    fuel_expenses = models.FloatField(default=0.0, null=True, blank=True)
    entertaiment_expenses = models.FloatField(default=0.0, null=True, blank=True)
    other_expenses = models.FloatField(default=0.0, null=True, blank=True)