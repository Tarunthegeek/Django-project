"""Views for accounts — register, login, logout."""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from .forms import RegistrationForm, LoginForm


class RegisterView(View):
    template_name = 'accounts/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = RegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'user'
            user.is_approved = False
            user.save()
            messages.success(
                request,
                '✅ Account created! Please wait for admin approval before logging in.'
            )
            return redirect('login')
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is None:
                messages.error(request, '❌ Invalid username or password.')
                return render(request, self.template_name, {'form': form})

            if not user.is_approved:
                messages.error(
                    request,
                    '⏳ Your account is pending admin approval. Please try again later.'
                )
                return render(request, self.template_name, {'form': form})

            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')

        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('login')
