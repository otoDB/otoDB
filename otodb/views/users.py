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

class RegisterForm(forms.Form):
    username = forms.CharField(label="Username", required=True)
    email = forms.CharField(label="Email", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, required=True)

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
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            if confirm_password == password:
                user = Account.objects.create_user(username, email, password=password)
                login(request, user)
                return redirect('otodb:index')
            else:
                form.add_error(None, "Passwords do not match")
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})

def profile(request: HttpRequest, user_id: int):
    user = get_object_or_404(Account, pk=user_id)
    return render(request, "users/profile.html", {'view_user': user})

def lists(request: HttpRequest, user_id: int):
    user = get_object_or_404(Account, pk=user_id)
    lists = user.pool_set.all()
    return render(request, 'users/lists.html', {'view_user': user, 'lists': lists})
