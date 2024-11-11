from django.urls import path
from . import views

urlpatterns = [
    path('vouchers/', views.voucher_list, name="vouchers"),

    path('reports/', views.report_list, name="reports"),
    path('reports/receipt/<int:receipt_id>/pdf/', views.generate_pdf_receipt, name='generate_pdf_receipt'),
    
]
