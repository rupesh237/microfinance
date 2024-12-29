
from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoanListView.as_view(), name='loans'),

    path('member/<int:member_id>/loans/', views.member_loans, name='member_loans'),
    path('update-member-info-for-loan/<int:member_id>', views.UpdateMemberInfoforLoan.as_view(views.FORMSS), name='update_member_for_loans'),
    path('take-loan/<int:member_id>', views.take_loan, name='take_loan'),

    path('update_address/<int:member_id>/', views.update_address_info, name='update_member_for_loan'),
    path('update_personal/<int:member_id>/', views.UpdatePersonalInfoView.as_view(), name='update_personal_info_for_loan'),
    path('update-family-info/<int:member_id>/', views.update_family_info_view, name='update_family_info_for_loan'),    
    path('update-livestock/<int:member_id>/', views.update_livestock_info_view, name='update_livestock_info_for_loan'),
    path('update-house/<int:member_id>/', views.update_house_info_view, name='update_house_info_for_loan'),
    path('update-land/<int:member_id>/', views.update_land_info_view, name='update_land_info_for_loan'),
    path('update_income/<int:member_id>/', views.update_income_info, name='update_income_info_for_loan'),
    path('update_expenses/<int:member_id>/', views.update_expenses_info, name='update_expenses_info_for_loan'),

    path('take-loan-form/<int:member_id>', views.loan_demand_form, name= 'loan_demand_form'),
    path('<int:member_id>/loan-demand/', views.loan_demand_list, name= 'loan_demand_list'),
    
    path('loan-analysis/<int:loan_id>', views.loan_analysis_form, name= 'loan_analysis_form'),
    path('<int:member_id>/loan-analysis', views.loan_analysis_list, name= 'loan_analysis_list'),

    path("loans/preview-schedule/", views.preview_schedule, name="loan_preview_schedule"),
    path('loan-disburse/<int:loan_id>', views.loan_disburse_form, name= 'loan_disburse_form'),
    path('<int:member_id>/loan-disburse', views.loan_disburse_list, name= 'loan_disburse_list'),

    path('approve/<int:loan_id>', views.approve_loan, name= 'approve_loan'),
    path('loan-payment/<int:loan_id>', views.loan_payment, name= 'loan_payment'),
    path('<int:member_id>/loan-payment', views.loan_payment_list, name= 'loan_payment_list'),
    
    # need to chanage this url for better printing options with proper css
    path('download-pdf-report/<int:member_id>', views.pdf_report, name='download_pdf_report'),
    path('confirm-clear-loan/<int:loan_id>/', views.confirm_clear_loan, name='confirm_clear_loan'),
    path('cleared-loans/<int:member_id>/', views.cleared_loans, name='cleared_loans'),
]
