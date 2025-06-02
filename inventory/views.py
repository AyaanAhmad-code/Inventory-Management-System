from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST

from .forms import LoginForm
from .forms import (
    CreateUserForm
)

def register(request):
    """
    Handle user registration.
    If the request is POST, process the form data to create a new user.
    Redirect to the login page on successful registration.
    For GET requests, render the registration form.
    """
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users-login')
    else:
        form = CreateUserForm()

    return render(request, 'users/register.html', {'form': form})

def login_page(request):
    forms = LoginForm()
    if request.method == 'POST':
        forms = LoginForm(request.POST)
        if forms.is_valid():
            username = forms.cleaned_data['username']
            password = forms.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
        else:
            # Form is invalid, errors will be in form.errors
            print(forms.errors)  # Add this for debugging
    context = {'form': forms}
    return render(request, 'users/login.html', context)


def logout_page(request):
    logout(request)
    return redirect('users-login')