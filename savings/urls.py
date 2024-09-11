# savings/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('member/<int:member_id>/savings/', views.member_savings, name='member_savings'),
    path('member/<int:member_id>/savings/add/', views.add_savings_account, name='add_savings_account'),
    path('member/<int:member_id>/fixed-deposit/add/', views.add_fixed_deposit, name='add_fixed_deposit'),
    path('member/<int:member_id>/recurring-deposit/add/', views.add_recurring_deposit, name='add_recurring_deposit'),
]
