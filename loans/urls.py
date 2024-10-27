
from django.urls import path
from . import views

urlpatterns = [
    path('member/<int:member_id>/loans/', views.member_loans, name='member_loans'),
    path('update-member-info-for-loan/<int:member_id>', views.UpdateMemberInfoforLoan.as_view(views.FORMSS), name='update_member_for_loan'),
    path('take-loan/<int:member_id>', views.take_loan, name='take_loan'),
    path('take-loan-form/<int:member_id>', views.loan_form, name= 'loan_form'),
    # need to chanage this url for better printing options with proper css
    path('download-pdf-report/<int:member_id>', views.pdf_report, name='download_pdf_report'),
]
