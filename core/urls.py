from django.urls import path
from . import views

urlpatterns = [
    path('vouchers/', views.voucher_list, name="vouchers"),
    path('voucher/add/', views.add_voucher, name="new_voucher"),
    path('voucher/add/receipt/', views.create_receipt, name="new_receipt"),
    path('voucher/add/payment/', views.create_payment, name="new_payment"),
    path('voucher/add/journal/', views.create_journal, name="new_journal"),

    path('collection-sheet-by-date/', views.collection_sheet_by_date, name='collection_sheet_by_date'),
    path('collection-sheet-by-center/', views.collection_sheet_by_center, name='collection_sheet_by_center'),

    path('collection-sheet/create/<int:center_id>', views.create_collection_sheet, name='create_collection_sheet'),
    path('collection-sheet/<int:center_id>', views.collection_sheet_view, name='collection_sheet'),
    path('collection-sheet/pdf/<int:center_id>/', views.collection_sheet_pdf, name='collection_sheet_pdf'),

    path('reports/', views.report_list, name="reports"),
    path('reports/daybook/', views.day_book_report, name='generate_pdf_daybook'),  
    path('reports/receipt/', views.receipt_compile_report, name='generate_pdf_receipt'),  
    path('reports/payment/', views.payment_compile_report, name='generate_pdf_payment'),  

    path('cash-management/', views.cash_management_view, name="cash_management_view"),
    path('cash-management/teller/<int:transaction_id>/approve', views.update_teller_transaction, name="update_teller_transaction"),
    path('cash-management/vault/<int:transaction_id>/approve', views.update_vault_transaction, name="update_vault_transaction"),

    path('member-chart/', views.member_chart, name='member_chart'),
    path('saving-chart/', views.savings_chart, name='saving_chart'),
    path('loan-outstanding-chart/', views.loan_outstanding_chart, name='loan_outstanding_chart'),
    path('loan-disburse-chart/', views.loan_disburse_chart, name='loan_disburse_chart'),
]
