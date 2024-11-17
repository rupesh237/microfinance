# savings/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('member/<int:member_id>/savings/', views.member_savings, name='member_savings'),
    path('member/<int:member_id>/savings/add/', views.add_savings_account, name='add_savings_account'),
    path('member/<int:member_id>/fixed-deposit/add/', views.add_fixed_deposit, name='add_fixed_deposit'),
    path('member/<int:member_id>/recurring-deposit/add/', views.add_recurring_deposit, name='add_recurring_deposit'),

    path('member/<int:member_id>/cash-sheet/create/', views.CashSheetCreateView.as_view(), name='create_cash_sheet'),
    path('member/<int:member_id>/cash-sheet/delete/<int:pk>/', views.delete_cash_sheet, name='delete_cash_sheet'),

    path('member/<int:member_id>/payment-sheet/create/', views.PaymentSheetCreateView.as_view(), name='create_payment_sheet'),
    path('member/<int:member_id>/payment-sheet/delete/<int:pk>/', views.delete_payment_sheet, name='delete_payment_sheet'),

    path('member/<int:member_id>/statements/', views.statement_list, name='member-statement'),
    path('member/<int:member_id>/statement/pdf/', views.statement_pdf_view, name='statement_pdf'),
]
