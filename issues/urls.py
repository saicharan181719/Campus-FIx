from django.urls import path

from .views import (
    issue_detail,
    issue_list,
    report_issue,
    maintenance_dashboard,
    maintenance_update_issue,
    admin_dashboard,
    admin_issues,
    admin_issue_detail,
    admin_users,
    admin_maintenance,
    admin_categories,
    admin_locations,
    admin_reports,
)


urlpatterns = [
    path(
        'student/',
        issue_list,
        name='issue_list'
    ),

    path(
        'report/',
        report_issue,
        name='report_issue'
    ),

    path(
        'issue/<int:pk>/',
        issue_detail,
        name='issue_detail'
    ),

    path(
        'maintenance/',
        maintenance_dashboard,
        name='maintenance_dashboard'
    ),

    path(
        'maintenance/issue/<int:pk>/update/',
        maintenance_update_issue,
        name='maintenance_update_issue'
    ),
    path(
    'admin-dashboard/',
    admin_dashboard,
    name='admin_dashboard'
),

path(
    'admin-dashboard/issues/',
    admin_issues,
    name='admin_issues'
),

path(
    'admin-dashboard/issues/<int:pk>/',
    admin_issue_detail,
    name='admin_issue_detail'
),

path(
    'admin-dashboard/users/',
    admin_users,
    name='admin_users'
),

path(
    'admin-dashboard/maintenance/',
    admin_maintenance,
    name='admin_maintenance'
),

path(
    'admin-dashboard/categories/',
    admin_categories,
    name='admin_categories'
),

path(
    'admin-dashboard/locations/',
    admin_locations,
    name='admin_locations'
),

path(
    'admin-dashboard/reports/',
    admin_reports,
    name='admin_reports'
),

]