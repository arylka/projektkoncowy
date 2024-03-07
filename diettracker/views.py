import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectdjango.settings')
django.setup()
from django.shortcuts import render, redirect
from matplotlib.figure import Figure
import io
import random
from datetime import datetime, timedelta, date
from django.db.models import Max, Min
from django.db import IntegrityError
import tempfile
from django.urls import reverse_lazy, reverse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from diettracker.models import Food, Consumption, Diet, WeightEntry, Meal, UserMeal
from diettracker.forms import LoginForm, RegisterForm, DietForm, WeightUpdateForm, DietForm, BMICalculatorForm, ConsumptionForm, MealForm, EditMealForm, MealConsumptionForm, AddMealForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormMixin
from django.shortcuts import get_object_or_404

class HomeView(View):
    def get(self, request):
        return render(request, 'base.html')

class SuccessView(View):
    def get(self, request):
        return render(request, 'success.html')

class ProfileView(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    def get(self, request):
        return render(request, 'profile.html')

class DietView(View):
    def get(self, request):
        return render(request, 'diets.html')

class LoginView(View):
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                messages.error(request, 'Nieprawidłowe dane logowania.')
        return render(request, 'login.html', {'form': form})

    def get(self, request):
        form = LoginForm()
        return render(request, 'login.html', {'form': form})


class BMIView(View):
    def get(self, request):
        form = BMICalculatorForm()
        return render(request, 'bmi.html', {'form': form})




class ConsumptionView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        today_consumption = Consumption.objects.filter(user=user, date=date.today()).values('calories', 'fat', 'carbohydrates', 'protein')
        total_calories = sum(item['calories'] for item in today_consumption)
        total_fat = sum(item['fat'] for item in today_consumption)
        total_carbohydrates = sum(item['carbohydrates'] for item in today_consumption)
        total_protein = sum(item['protein'] for item in today_consumption)

        user_diet = Diet.objects.filter(user=user).first()

        remaining_calories = max(0, user_diet.max_calories - total_calories) if user_diet and user_diet.max_calories is not None else None
        remaining_fat = user_diet.max_fat - total_fat if user_diet and user_diet.max_fat is not None else None
        remaining_carbohydrates = max(0, user_diet.max_carbohydrates - total_carbohydrates) if user_diet and user_diet.max_carbohydrates is not None else None
        remaining_protein = max(0, user_diet.max_protein - total_protein) if user_diet and user_diet.max_protein is not None else None

        consumption_form = ConsumptionForm()
        meal_consumption_form = MealConsumptionForm(user=user)

        context = {
            'form': consumption_form,
            'meal_consumption_form': meal_consumption_form,
            'total_calories': total_calories,
            'total_fat': total_fat,
            'total_carbohydrates': total_carbohydrates,
            'total_protein': total_protein,
            'remaining_calories': remaining_calories,
            'remaining_fat': remaining_fat,
            'remaining_carbohydrates': remaining_carbohydrates,
            'remaining_protein': remaining_protein
        }
        return render(request, 'consumption.html', context)

    def post(self, request):
        consumption_form = ConsumptionForm(request.POST)
        meal_consumption_form = MealConsumptionForm(request.POST, user=request.user)

        if 'meal' in request.POST:
            if meal_consumption_form.is_valid():
                user_id = request.user.id
                meal_id = meal_consumption_form.cleaned_data['meal'].id
                meal = Meal.objects.get(pk=meal_id)
                amount = 1
                calories = meal.calories
                fat = meal.fat if meal.fat is not None else 0
                carbohydrates = meal.carbohydrates if meal.carbohydrates is not None else 0
                protein = meal.protein if meal.protein is not None else 0
                name = meal.name
                consumption = Consumption.objects.create(user_id=user_id, date=date.today(), calories=calories, fat=fat,
                                                         carbohydrates=carbohydrates, protein=protein, name=name)
                return redirect('consumption')

        elif 'food' in request.POST:
            if consumption_form.is_valid():
                user_id = request.user.id
                food = consumption_form.cleaned_data['food']
                amount = consumption_form.cleaned_data['amount']
                calories = (food.calories / 100) * amount
                fat = (food.fat / 100) * amount
                carbohydrates = (food.carbohydrates / 100) * amount
                protein = (food.protein / 100) * amount
                name = f"{food.name} ({amount}g)"
                consumption = Consumption.objects.create(user_id=user_id, date=date.today(), calories=calories, fat=fat,
                                                         carbohydrates=carbohydrates, protein=protein, name=name)
                return redirect('consumption')

        elif 'consumption_id' in request.POST:
            consumption_id = request.POST.get('consumption_id')
            if consumption_id:
                try:
                    consumption = Consumption.objects.get(pk=consumption_id)
                except Consumption.DoesNotExist:
                    return HttpResponseBadRequest("Invalid consumption ID")
            else:
                return HttpResponseBadRequest("Missing consumption ID")

        return HttpResponseBadRequest("Błąd przetwarzania formularza")


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            User.objects.create_user(username=username, password=password)
            return redirect('success')
        return render(request, 'register.html', {'form': form})



def update_diet(request):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    user = request.user
    try:
        diet = Diet.objects.get(user=user)
        form = DietForm(request.POST or None, instance=diet)
    except Diet.DoesNotExist:
        form = DietForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            diet = form.save(commit=False)
            diet.user = user
            diet.save()
            return redirect('success')
    return render(request, 'update_diet.html', {'form': form})

class WeightUpdateView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = WeightUpdateForm()
        return render(request, 'update_weight.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = WeightUpdateForm(request.POST)
        if form.is_valid():
            weight = form.cleaned_data['weight']
            user = request.user
            today = timezone.now().date()
            try:
                existing_weight = WeightEntry.objects.get(user=user, date=today)
                existing_weight.weight = weight
                existing_weight.save()
            except WeightEntry.DoesNotExist:
                WeightEntry.objects.create(user=user, date=today, weight=weight)
            return redirect('success')
        return render(request, 'update_weight.html', {'form': form})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


class WeightChartView(LoginRequiredMixin, View):
    def get(self, request):
        weight_entries = WeightEntry.objects.filter(user=request.user)

        if len(weight_entries) < 2 or weight_entries.aggregate(earliest_date=Min('date'), latest_date=Max('date'))['earliest_date'] == weight_entries.aggregate(earliest_date=Min('date'), latest_date=Max('date'))['latest_date']:
            return render(request, 'weight_chart.html', {'chart_data': None})
        else:
            dates = [entry.date for entry in weight_entries]
            weights = [entry.weight for entry in weight_entries]

            plt.plot(dates, weights)
            plt.xlabel('Data')
            plt.ylabel('Waga')
            plt.title('Waga w zależności od czasu')

            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                chart_path = temp_file.name
                plt.savefig(chart_path)

            with open(chart_path, 'rb') as f:
                chart_data = f.read()

            response = HttpResponse(chart_data, content_type='image/png')
            return response
class FoodView(ListView):
    model = Food
    template_name = 'food.html'
    context_object_name = 'foods'

'''
class WeightHistoryListView(ListView):
    model = WeightEntry
    template_name = 'weight_history.html'

    def get_queryset(self):
        user = self.request.user

        start_date = datetime(2024, 2, 10).date()
        end_date = datetime(2024, 2, 22).date()
        current_date = start_date

        while current_date <= end_date:
            existing_entry = WeightEntry.objects.filter(user=user, date=current_date).first()
            if not existing_entry:
                random_weight = round(random.uniform(66.0, 67.0), 1)
                WeightEntry.objects.create(user=user, date=current_date, weight=random_weight)
            current_date += timedelta(days=1)

        return WeightEntry.objects.filter(user=user).order_by('-date')
'''


class MealListView(LoginRequiredMixin, ListView):
    model = Meal
    template_name = 'meal.html'
    context_object_name = 'meals'

    def get_queryset(self):
        return Meal.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MealForm()
        return context

    def post(self, request, *args, **kwargs):
        form = MealForm(request.POST)
        if form.is_valid():
            calories = form.cleaned_data['calories']
            protein = form.cleaned_data['protein']
            carbohydrates = form.cleaned_data['carbohydrates']
            fat = form.cleaned_data['fat']

            if (calories is not None and calories > 4999) or protein is not None and protein > 999 or carbohydrates is not None and carbohydrates > 999 or fat is not None and fat > 999:
                return HttpResponseBadRequest("Wartości kalorii i makroskładników nie mogą przekroczyć odpowiednich limitów.")

            meal = form.save(commit=False)
            meal.user = request.user
            meal.save()
            return redirect('meal_list')
        else:
            return HttpResponseBadRequest("Błąd przetwarzania formularza.")

class MealEditView(LoginRequiredMixin, UpdateView):
    model = Meal
    form_class = EditMealForm
    template_name = 'meal_edit.html'
    success_url = reverse_lazy('meal_list')

    def get_queryset(self):
        return Meal.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object() if self.object else None
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class MealDeleteView(LoginRequiredMixin, DeleteView):
    model = Meal
    success_url = reverse_lazy('meal_list')

    def get_queryset(self):
        return Meal.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()

class ConsumptionListView(LoginRequiredMixin, View):
    def get(self, request):
        user_id = request.user.id

        today_consumption = Consumption.objects.filter(user_id=user_id, date=timezone.now().date())

        context = {
            'today_consumption': today_consumption,
        }
        return render(request, 'consumption_list.html', context)

    def post(self, request):
        if 'delete_consumption' in request.POST:
            consumption_id = request.POST.get('delete_consumption')
            try:
                consumption = Consumption.objects.get(id=consumption_id)
                consumption.delete()
            except Consumption.DoesNotExist:
                pass
        return HttpResponseRedirect(reverse('consumption_list'))


class AllMealsView(ListView):
    model = Meal
    template_name = 'all_meals.html'
    context_object_name = 'meals'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_meal_form'] = AddMealForm()
        return context

    def post(self, request, *args, **kwargs):
        form = AddMealForm(request.POST)
        if form.is_valid():
            meal_id = form.cleaned_data['meal_id']
            user = request.user
            try:
                meal = Meal.objects.get(pk=meal_id)
                UserMeal.objects.create(user=user, meal=meal)
            except Meal.DoesNotExist:
                pass
            except IntegrityError:
                return HttpResponseBadRequest("Posiłek został już dodany do Twojej listy.")
        return super().get(request, *args, **kwargs)
