from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect

from .models import Employee

class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = ['admin', 'manager', 'superuser']

    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        try:
            employee = user.employee
            return employee.role in self.allowed_roles
        except Employee.DoesNotExist:
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('dashboard')
