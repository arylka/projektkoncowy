"""
URL configuration for projectdjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from diettracker import views
from diettracker.views import (LoginView, RegisterView, SuccessView, ProfileView, WeightUpdateView, ConsumptionView, update_diet, LogoutView, WeightChartView, HomeView, DietView,
                               BMIView, FoodView, MealListView, MealEditView, MealDeleteView, ConsumptionListView, AllMealsView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HomeView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('success/', SuccessView.as_view(), name='success'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('update_weight/',WeightUpdateView.as_view(), name='update_weight'),
    path('consumption/',ConsumptionView.as_view(), name='consumption'),
    path('update_diet/', update_diet, name='update_diet'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('weight_chart/', WeightChartView.as_view(), name='weight_chart'),
    path('diets/', DietView.as_view(), name='diets'),
    path('bmi/', BMIView.as_view(), name='bmi'),
    path('food/', FoodView.as_view(), name='food'),
    path('meal/', MealListView.as_view(), name='meal_list'),
    path('meal/<int:pk>/edit/', MealEditView.as_view(), name='meal_edit'),
    path('meal/<int:pk>/delete/', MealDeleteView.as_view(), name='meal_delete'),
    path('consumption_list/', ConsumptionListView.as_view(), name='consumption_list'),
    path('all_meals', AllMealsView.as_view(), name='all_meals'),
]

