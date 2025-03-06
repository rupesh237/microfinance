from django.contrib import admin
from .forms import EmployeeForm, BranchForm

# Register your models here.
from .models import Province, District, Municipality, Employee, Branch, Center, GRoup, AddressInformation, PersonalInformation, PersonalMemberDocument, FamilyMemberDocument,IncomeInformation, LandInformation, FamilyInformation, Member, LivestockInformation, ExpensesInformation, HouseInformation

class BranchAdmin(admin.ModelAdmin):
    form = BranchForm

class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeForm
    list_display = ('user', 'branch', 'role')

    # def save_model(self, request, obj, form, change):
    #     if not change:  # If this is a new Employee instance
    #         obj.user.set_password('defaultpassword')  # Set a default password
    #         obj.user.save()
    #     super().save_model(request, obj, form, change)

admin.site.register(Province)
admin.site.register(District)
admin.site.register(Municipality)
admin.site.register(Branch, BranchAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Center)
admin.site.register(GRoup)
admin.site.register(AddressInformation)
admin.site.register(HouseInformation)
admin.site.register(IncomeInformation)
admin.site.register(ExpensesInformation)
admin.site.register(Member)
admin.site.register(LandInformation)
admin.site.register(LivestockInformation)
admin.site.register(PersonalInformation)
admin.site.register(FamilyInformation)
admin.site.register(PersonalMemberDocument)
admin.site.register(FamilyMemberDocument)