from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User

from .forms import IssueForm, IssueUpdateForm, StudentVerificationForm, AdminIssueUpdateForm, CategoryForm, LocationForm
from .models import Issue, IssueUpdate, Category, Location
from accounts.forms import AdminUserForm
from django.db.models import Count, Q

CATEGORY_SPECIALIZATION_MAP = {
    'Electrical': 'electrical',
    'Plumbing': 'plumbing',
    'Cleaning': 'cleaning',
    'Wi-Fi/IT': 'it',
    'Classroom Equipment': 'equipment',
    'Security': 'security',
    'Other': 'other',
}


@login_required
def issue_list(request):
    if request.user.role == 'maintenance':
        return redirect('maintenance_dashboard')

    if request.user.role == 'admin':
        return redirect('admin_dashboard')

    issues = Issue.objects.filter(
        reporter=request.user
    ).order_by('-created_at')

    return render(
        request,
        'issues/home.html',
        {'issues': issues}
    )

@login_required
def report_issue(request):
    if request.user.role != 'student':
        if request.user.role == 'maintenance':
            return redirect('maintenance_dashboard')

        if request.user.role == 'admin':
            return redirect('admin_dashboard')
    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES)

        if form.is_valid():
            issue = form.save(commit=False)

            issue.reporter = request.user

            specialization = CATEGORY_SPECIALIZATION_MAP.get(
    issue.category.name
)

            # Automatically assign maintenance user
            maintenance_user = User.objects.filter(
                role='maintenance',
                specialization=specialization,
                is_active=True
            ).first()

            if maintenance_user:
                issue.assigned_to = maintenance_user

            issue.save()

            return redirect(
                'issue_detail',
                pk=issue.pk
            )

    else:
        form = IssueForm()

    return render(
        request,
        'issues/report_issue.html',
        {'form': form}
    )


@login_required
def issue_detail(request, pk):
    if request.user.role == 'admin':
        return redirect(
            'admin_issue_detail',
            pk=pk
        )

    if request.user.role == 'student':
        issue = get_object_or_404(
            Issue,
            pk=pk,
            reporter=request.user
        )

    elif request.user.role == 'maintenance':
        issue = get_object_or_404(
            Issue,
            pk=pk,
            assigned_to=request.user
        )

    else:
        return redirect('issue_list')

    updates = issue.updates.select_related(
        'updated_by'
    ).order_by('created_at')

    return render(
        request,
        'issues/issue_detail.html',
        {
            'issue': issue,
            'updates': updates,
        }
    )

@login_required
def student_verify_issue(request, pk):
    if request.user.role != 'student':
        return redirect('issue_list')

    issue = get_object_or_404(
        Issue,
        pk=pk,
        reporter=request.user
    )

    # Student can verify only resolved issues
    if issue.status != 'resolved':
        return redirect('issue_detail', pk=pk)

    if request.method == 'POST':
        form = StudentVerificationForm(request.POST, instance=issue)

        if form.is_valid():
            issue = form.save(commit=False)

            if issue.student_verified:
                issue.status = 'closed'
            else:
                issue.status = 'reopened'

            issue.save()

            IssueUpdate.objects.create(
                issue=issue,
                updated_by=request.user,
                status=issue.status,
                comment=(
                    'Student confirmed the issue is resolved.'
                    if issue.student_verified
                    else 'Student reported that the issue is not fixed and requested reopening.'
                )
            )

            return redirect('issue_detail', pk=issue.pk)

    else:
        form = StudentVerificationForm(instance=issue)

    return render(
        request,
        'issues/student_verify.html',
        {
            'issue': issue,
            'form': form,
        }
    )

@login_required
def maintenance_dashboard(request):
    if request.user.role != 'maintenance':
        return redirect('issue_list')

    issues = Issue.objects.filter(
        assigned_to=request.user
    ).order_by('-created_at')

    return render(
        request,
        'maintenance/dashboard.html',
        {'issues': issues}
    )
@login_required
def maintenance_update_issue(request, pk):

    if request.user.role != 'maintenance':
        return redirect('issue_list')

    issue = get_object_or_404(
        Issue,
        pk=pk,
        assigned_to=request.user
    )

    if request.method == 'POST':
        form = IssueUpdateForm(request.POST, request.FILES, instance=issue)

        if form.is_valid():

            old_status = issue.status

            issue = form.save()

            if old_status != issue.status:
                IssueUpdate.objects.create(
                    issue=issue,
                    updated_by=request.user,
                    status=issue.status,
                    comment=(
                        f'Status changed from '
                        f'{old_status} to {issue.status}.'
                    )
                )

            return redirect(
                'maintenance_dashboard'
            )

    else:
        form = IssueUpdateForm(instance=issue)

    return render(
        request,
        'maintenance/update_issue.html',
        {
            'issue': issue,
            'form': form,
        }
    )
@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('issue_list')

    total_issues = Issue.objects.count()

    open_issues = Issue.objects.filter(
        status__in=['reported', 'reviewed', 'assigned']
    ).count()

    in_progress_issues = Issue.objects.filter(
        status='in_progress'
    ).count()

    resolved_issues = Issue.objects.filter(
        status='resolved'
    ).count()

    closed_issues = Issue.objects.filter(
        status='closed'
    ).count()

    unassigned_issues = Issue.objects.filter(
        assigned_to__isnull=True
    ).count()

    recent_issues = Issue.objects.select_related(
        'category',
        'location',
        'reporter',
        'assigned_to'
    ).order_by('-created_at')[:5]

    context = {
        'total_issues': total_issues,
        'open_issues': open_issues,
        'in_progress_issues': in_progress_issues,
        'resolved_issues': resolved_issues,
        'closed_issues': closed_issues,
        'unassigned_issues': unassigned_issues,
        'recent_issues': recent_issues,
    }

    return render(
        request,
        'admin/dashboard.html',
        context
    )

@login_required
def admin_issues(request):
    if request.user.role != 'admin':
        return redirect('issue_list')

    issues = Issue.objects.select_related(
        'category',
        'location',
        'reporter',
        'assigned_to'
    ).order_by('-created_at')

    # Search
    search = request.GET.get('search', '').strip()

    if search:
        from django.db.models import Q

        issues = issues.filter(
            Q(ticket_id__icontains=search) |
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    # Status filter
    status = request.GET.get('status', '').strip()

    if status:
        issues = issues.filter(status=status)

    # Category filter
    category = request.GET.get('category', '').strip()

    if category:
        issues = issues.filter(category_id=category)

    # Priority filter
    priority = request.GET.get('priority', '').strip()

    if priority:
        issues = issues.filter(priority=priority)

    # Location filter
    location = request.GET.get('location', '').strip()

    if location:
        issues = issues.filter(location_id=location)

    # Date filter
    date = request.GET.get('date', '').strip()

    if date:
        issues = issues.filter(created_at__date=date)

    return render(
        request,
        'admin/issues.html',
        {
            'issues': issues,
            'categories': Category.objects.all(),
            'locations': Location.objects.all(),
            'status_choices': Issue.STATUS_CHOICES,
            'priority_choices': Issue.PRIORITY_CHOICES,

            # Keep filter values selected after searching
            'search': search,
            'selected_status': status,
            'selected_category': category,
            'selected_priority': priority,
            'selected_location': location,
            'selected_date': date,
        }
    )
@login_required
def admin_issue_detail(request, pk):
    if request.user.role != 'admin':
        return redirect('issue_list')

    issue = get_object_or_404(
        Issue.objects.select_related(
            'category',
            'location',
            'reporter',
            'assigned_to'
        ),
        pk=pk
    )

    if request.method == 'POST':
        form = AdminIssueUpdateForm(
            request.POST,
            instance=issue
        )

        if form.is_valid():
            old_status = issue.status
            old_assigned_to = issue.assigned_to

            issue = form.save()

            # Status changed
            if old_status != issue.status:
                IssueUpdate.objects.create(
                    issue=issue,
                    updated_by=request.user,
                    status=issue.status,
                    comment=(
                        f'Admin changed status from '
                        f'{old_status} to {issue.status}.'
                    )
                )

            # Assignment changed
            if old_assigned_to != issue.assigned_to:
                old_name = (
                    old_assigned_to.username
                    if old_assigned_to
                    else 'Unassigned'
                )

                new_name = (
                    issue.assigned_to.username
                    if issue.assigned_to
                    else 'Unassigned'
                )

                IssueUpdate.objects.create(
                    issue=issue,
                    updated_by=request.user,
                    status=issue.status,
                    comment=(
                        f'Issue reassigned from '
                        f'{old_name} to {new_name}.'
                    )
                )

            return redirect(
                'admin_issue_detail',
                pk=issue.pk
            )

    else:
        form = AdminIssueUpdateForm(
            instance=issue
        )

    updates = issue.updates.select_related(
        'updated_by'
    ).order_by('created_at')

    return render(
        request,
        'admin/issue_detail.html',
        {
            'issue': issue,
            'updates': updates,
            'form': form,
        }
    )

@login_required
def admin_users(request):
    if request.user.role != 'admin':
        return redirect('issue_list')

    if request.method == 'POST':
        form = AdminUserForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('admin_users')

    else:
        form = AdminUserForm()

    users = User.objects.all().order_by(
        'role',
        'username'
    )

    return render(
        request,
        'admin/users.html',
        {
            'users': users,
            'form': form,
        }
    )

@login_required
def admin_maintenance(request):
    if request.user.role != 'admin':
        return redirect('issue_list')

    maintenance_users = User.objects.filter(
        role='maintenance'
    ).prefetch_related(
        'assigned_issues'
    ).order_by(
        'specialization',
        'username'
    )

    return render(
        request,
        'admin/maintenance.html',
        {
            'maintenance_users': maintenance_users,
        }
    )

@login_required
def admin_categories(request):
    if request.user.role != 'admin':
        return redirect('issue_list')

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('admin_categories')
    else:
        form = CategoryForm()

    categories = Category.objects.prefetch_related(
        'issues'
    ).order_by('name')

    return render(
        request,
        'admin/categories.html',
        {
            'categories': categories,
            'form': form,
        }
    )

@login_required
def admin_locations(request):
    if request.user.role != 'admin':
        return redirect('issue_list')

    if request.method == 'POST':
        form = LocationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('admin_locations')
    else:
        form = LocationForm()

    locations = Location.objects.prefetch_related(
        'issues'
    ).order_by(
        'block',
        'building',
        'room'
    )

    return render(
        request,
        'admin/locations.html',
        {
            'locations': locations,
            'form': form,
        }
    )

@login_required
def admin_reports(request):
    if request.user.role != 'admin':
        return redirect('issue_list')

    total_issues = Issue.objects.count()

    open_issues = Issue.objects.filter(
        status__in=['reported', 'reviewed', 'assigned']
    ).count()

    in_progress_issues = Issue.objects.filter(
        status='in_progress'
    ).count()

    resolved_issues = Issue.objects.filter(
        status='resolved'
    ).count()

    # -------------------------
    # Issues by Category
    # -------------------------

    category_data = Category.objects.annotate(
        issue_count=Count('issues')
    ).order_by('-issue_count')

    category_report = []

    for category in category_data:
        percentage = (
            (category.issue_count / total_issues) * 100
            if total_issues > 0
            else 0
        )

        category_report.append({
            'name': category.name,
            'count': category.issue_count,
            'percentage': round(percentage, 1),
        })
        
        category_report = []

    for category in category_data:
        if total_issues > 0:
            percentage = round(
                (category.issue_count * 100) / total_issues,
                1
            )
        else:
            percentage = 0

        category_report.append({
            'name': category.name,
            'count': category.issue_count,
            'percentage': percentage,
        })

    # -------------------------
    # Issues by Priority
    # -------------------------

    priority_data = Issue.objects.values(
        'priority'
    ).annotate(
        issue_count=Count('id')
    ).order_by('-issue_count')

    priority_report = []

    priority_names = dict(Issue.PRIORITY_CHOICES)

    for item in priority_data:
        priority_report.append({
            'name': priority_names.get(
                item['priority'],
                item['priority']
            ),
            'count': item['issue_count'],
        })

    # -------------------------
    # Issues by Location
    # -------------------------

    location_data = Location.objects.annotate(
        issue_count=Count('issues')
    ).order_by('-issue_count')

    location_report = []

    for location in location_data:
        location_report.append({
            'location': str(location),
            'block': location.block,
            'building': location.building,
            'room': location.room,
            'count': location.issue_count,
        })

    context = {
        'total_issues': total_issues,
        'open_issues': open_issues,
        'in_progress_issues': in_progress_issues,
        'resolved_issues': resolved_issues,
        'category_report': category_report,
        'priority_report': priority_report,
        'location_report': location_report,
    }

    return render(
        request,
        'admin/reports.html',
        context
    )

@login_required
def faculty_dashboard(request):
    if request.user.role != 'faculty':
        return redirect('issue_list')

    issues = Issue.objects.select_related(
        'category',
        'location',
        'reporter',
        'assigned_to'
    ).order_by('-created_at')

    return render(
        request,
        'faculty/dashboard.html',
        {
            'issues': issues,
        }
    )

@login_required
def faculty_issue_detail(request, pk):
    if request.user.role != 'faculty':
        return redirect('issue_list')

    issue = get_object_or_404(
        Issue.objects.select_related(
            'category',
            'location',
            'reporter',
            'assigned_to'
        ),
        pk=pk
    )

    updates = issue.updates.select_related(
        'updated_by'
    ).order_by('created_at')

    return render(
        request,
        'faculty/issue_detail.html',
        {
            'issue': issue,
            'updates': updates,
        }
    )