from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User

from .forms import IssueForm, IssueUpdateForm
from .models import Issue, IssueUpdate

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
    issue = get_object_or_404(
        Issue,
        pk=pk,
        reporter=request.user
    )

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
        form = IssueUpdateForm(request.POST, instance=issue)

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