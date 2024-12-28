from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render

from otodb.account.models import Account
from otodb.models import Pool


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)

def login_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('otodb:index')
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('otodb:index')
            form.add_error(None, "Authentication failed")
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {"form": form})

@login_required
def logout_view(request: HttpRequest):
    logout(request)
    return redirect('otodb:index')

def register_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('otodb:index')
    return render(request, 'users/register.html')

def profile(request: HttpRequest, user_id: int):
    user = get_object_or_404(Account, pk=user_id)
    return render(request, "users/profile.html", {'view_user': user})

def lists(request: HttpRequest, user_id: int):
    lists = Pool.objects.filter(author__pk=user_id)
    return render(request, 'users/lists.html', {'lists': lists})
