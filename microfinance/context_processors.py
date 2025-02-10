from dashboard.models import User, Employee

def branch_name(request):
    if request.user.is_authenticated:
        employee = Employee.objects.filter(user=request.user).first()
        if employee:
            return {'branch': employee.branch}
    return {}