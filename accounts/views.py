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


class UserLogoutView(LogoutView):
    next_page = 'login'