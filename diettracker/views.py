from django.shortcuts import render, redirect
from django.views import View
from diettracker.models import Food, Meal
from diettracker.forms import LoginForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

class HomeView(View):
    def get(self, request):
        return render(request, 'index.html')

class LoginView(View):
    def login_view(request):
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('home')
            else:
                form = LoginForm()
            return render(request, 'login.html')
