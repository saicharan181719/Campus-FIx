from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import UserRegistrationForm


def register(request):

    if request.user.is_authenticated:
        return redirect('issue_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect('issue_list')

    else:
        form = UserRegistrationForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form}
    )


class UserLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        portal = (
            self.request.GET.get('portal')
            or self.request.POST.get('portal')
            or 'student'
        )

        if portal not in [
            'student',
            'faculty',
            'maintenance',
            'admin'
        ]:
            portal = 'student'

        context['portal'] = portal

        return context

    def form_valid(self, form):
        portal = self.request.POST.get('portal', 'student')

        role_map = {
            'student': 'student',
            'faculty': 'faculty',
            'maintenance': 'maintenance',
            'admin': 'admin',
        }

        if portal not in role_map:
            form.add_error(
                None,
                'Invalid login portal.'
            )
            return self.form_invalid(form)

        user = form.get_user()

        if user.role != role_map[portal]:
            form.add_error(
                None,
                'This account does not have access to this portal.'
            )
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user

        if user.role == 'admin':
            return '/admin-dashboard/'

        elif user.role == 'maintenance':
            return '/maintenance/'

        elif user.role == 'faculty':
            return '/faculty/'

        return '/student/'


class UserLogoutView(LogoutView):
    next_page = '/'