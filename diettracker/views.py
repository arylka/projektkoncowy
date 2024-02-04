from django.shortcuts import render
from django.views import View
from diettracker.models import Food, Meal
from django.contrib.auth.decorators import login_required

class HomeView(View):
    def get(self, request):
        return render(request, 'index.html')



