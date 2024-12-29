from django.urls import path
from . import views

urlpatterns = [
    path('vouchers/', views.voucher_list, name="vouchers"),

    path('collection-sheet-by-date/', views.collection_sheet_by_date, name='collection_sheet_by_date'),
    path('collection-sheet-by-center/', views.collection_sheet_by_center, name='collection_sheet_by_center'),

    path('collection-sheet/create/<int:center_id>', views.create_collection_sheet, name='create_collection_sheet'),
    path('collection-sheet/<int:center_id>', views.collection_sheet_view, name='collection_sheet'),
    path('collection-sheet/pdf/<int:center_id>/', views.collection_sheet_pdf, name='collection_sheet_pdf'),

    path('reports/', views.report_list, name="reports"),
    path('reports/receipt/', views.receipt_compile_report, name='generate_pdf_receipt'),  
    path('reports/payment/', views.payment_compile_report, name='generate_pdf_payment'),  
]
