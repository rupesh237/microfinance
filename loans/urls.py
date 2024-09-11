
from django.urls import path
from . import views

urlpatterns = [
    path('member/<int:member_id>/loans/', views.member_loans, name='member_loans'),
]
