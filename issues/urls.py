from django.urls import path

from .views import (
    issue_detail,
    issue_list,
    report_issue,
    maintenance_dashboard,
    maintenance_update_issue,
)


urlpatterns = [
    path(
        '',
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
]