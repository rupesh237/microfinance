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
    path('branch/delete/<int:pk>/', views.delete_branch, name='delete_branch'),

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

    path('address-information/', views.AddressInfoView.as_view(), name = 'address_info'),
    path('personal-information/', views.PersonalInfoView.as_view(), name = 'personal_info'),
    path('family-information/', views.FamilyInfoView.as_view(), name = 'family_info'),
    path('get_new_family_form/', views.get_new_family_form, name='get_new_family_form'),
    path('livestock-information/', views.livestock_info_view, name = 'livestock_info'),
    path('house-information/', views.house_info_view, name = 'house_info'),
    path('land-information/', views.land_info_view, name = 'land_info'),
    path('income-information/', views.income_info_view, name = 'income_info'),
    path('expenses-information/', views.expenses_info_view, name = 'expenses_info'),

    # path('add-member/', views.MemberWizard.as_view(views.FORMS), name='add_member'),
    path('member/<int:member_id>/', views.member_detail_view, name='member_detail'),
    # path('update-member/<int:member_id>', views.MemberUpdateWizard.as_view(views.FORMSS), name='update_members'),
    
# update of member information urls
    path('update_address/<int:member_id>/', views.update_address_info, name='update_member'),
    path('update_personal/<int:member_id>/', views.UpdatePersonalInfoView.as_view(), name='update_personal_info'),
    path('update-family-info/<int:member_id>/', views.UpdateFamilyInfoView.as_view(), name='update_family_info'),    
    path('update-livestock/<int:member_id>/', views.update_livestock_info_view, name='update_livestock_info'),
    path('update-house/<int:member_id>/', views.update_house_info_view, name='update_house_info'),
    path('update-land/<int:member_id>/', views.update_land_info_view, name='update_land_info'),
    path('update_income/<int:member_id>/', views.update_income_info, name='update_income_info'),
    path('update_expenses/<int:member_id>/', views.update_expenses_info, name='update_expenses_info'),

    path('get_saving_accounts/<int:member_id>/', views.get_saving_accounts, name='get_saving_accounts'),
    path('members/', views.MemberListView.as_view(), name="member_list"),
    path('change_member_status/', views.change_member_status, name="change_member_status"),
    path('delete-member/<int:pk>/', views.MemberDeleteView.as_view(), name='delete_member'),

    path('deposits/', views.deposits, name='deposits'),
    path('transactions/', views.transactions, name='transactions'),
    path('reports/', views.reports, name='reports')
]