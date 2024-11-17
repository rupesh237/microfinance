from django.urls import path
from . import views

urlpatterns = [
    path('vouchers/', views.voucher_list, name="vouchers"),

    path('reports/', views.report_list, name="reports"),
    path('reports/receipt/', views.receipt_compile_report, name='generate_pdf_receipt'),  
    path('reports/payment/', views.payment_compile_report, name='generate_pdf_payment'),  
]
