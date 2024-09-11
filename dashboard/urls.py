from django.urls import path
from . import views

urlpatterns= [
    path('', views.user_login, name="login"),
    path('user/logout', views.user_logout, name="logout"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('dashboard/admin', views.admin_dashboard, name="admin_dashboard"),
    path('dashboard/manager', views.manager_dashboard, name ="manager_dashboard"),
    path('dashboard/employee', views.employee_dashboard, name='employee_dashboard'),

    path('add-employee', views.add_employee, name="add_employee"),
    path('employees/', views.employee_list_view, name='employee_list'),

    path('add-branch', views.add_branch, name="add_branch"),
    path('branches/', views.branch_list_view, name='branch_list'),
    path('branch/update/<int:pk>/', views.update_branch, name='update_branch'),

    path('ajax/load-districts', views.load_districts, name="load_districts"),
    path('ajax/load-municipalities', views.load_municipalities, name="load_municipalities"),
    path('ajax/load-branches', views.load_branches, name="load_branches"),
    
    path('add-center', views.CenterCreateView.as_view(), name="add_center"),
    path('centers/', views.CenterListView.as_view(), name='center_list'),
    path('edit-center/<int:pk>/', views.CenterUpdateView.as_view(), name='edit_center'),
    path('delete-center/<int:pk>/', views.CenterDeleteView.as_view(), name='delete_center'),

    path('get-center-code/<int:center_id>/', views.get_center_code, name='get-center-code'),
    path('get-no-of-groups/<int:center_id>/', views.get_no_of_groups, name='get-no-of-groups'),
    path('add-group/', views.GroupCreateView.as_view(), name="add_group"),
    path('groups/', views.GroupListView.as_view(), name='group_list'),
    path('edit-group/<int:pk>/', views.GroupUpdateView.as_view(), name='edit_group'),
    path('delete-group/<int:pk>/', views.GroupDeleteView.as_view(), name='delete_group'),

    # path('select-group/', views.select_group, name='select_group'),
    path('load-groups/', views.load_groups, name='load_groups'),
    path('load-member-codes/', views.load_member_codes, name='load_member_codes'), 
    path('select-center/', views.SelectCenterView.as_view(), name='select_center'),
    path('add-member/', views.MemberWizard.as_view(views.FORMS), name='add_member'),
    path('member/<int:member_id>/', views.member_detail_view, name='member_detail'),
    path('members/', views.member_list_view, name="member_list"),

    path('deposits/', views.deposits, name='deposits'),
    path('transactions/', views.transactions, name='transactions'),
    path('reports/', views.reports, name='reports')
]