from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from diettracker.models import Food, Meal, Consumption
from diettracker.forms import LoginForm
from diettracker.forms import RegisterForm

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


class BodyMassIndex:
    def calculate_bmi(self, weight, height_cm):
        height_m = height_cm / 100  # Konwersja wzrostu z centymetrów na metry
        bmi = weight / (height_m ** 2)

        if bmi < 18.5:
            category = 'Niedowaga'
        elif bmi < 24.9:
            category = 'Waga umiarkowana'
        elif bmi < 29.9:
            category = 'Nadwaga'
        else:
            category = 'Otyłość'

        return bmi, category

    def post(self, request):
        weight = float(request.POST.get('weight', 0))  # Pobierz wagę z żądania POST
        height_cm = float(request.POST.get('height_cm', 0))  # Pobierz wzrost z żądania POST

        if weight <= 0 or height_cm <= 0:
            return JsonResponse({'error': 'Waga i wzrost powinny być wartościami dodatnimi.'}, status=400)

        bmi, category = self.calculate_bmi(weight, height_cm)
        return JsonResponse({'result': f"Twoje BMI wynosi {bmi}, co oznacza, że zaliczasz się do kategorii {category}"})

class Macronutrients(View):
    def keto(self, request):
        user_id = request.session.get('user_id')

        # Pobierz obiekty Consumption dla danego użytkownika i daty
        try:
            consumption = Consumption.objects.get(user_id=user_id, date=date.today())
        except Consumption.DoesNotExist:
            return JsonResponse({'error': 'Brak danych dotyczących dzisiejszego spożycia dla użytkownika. Dzienny limit wynosi 50g węglowodanów'})

        carbohydrates = consumption.carbohydrates

        remaining_carbs = 50 - carbohydrates
        if carbohydrates < 50:
            return JsonResponse({'message': f"Możesz zjeść dziś jeszcze {remaining_carbs}g węglowodanów."})
        else:
            return JsonResponse({'message': "Dzienny limit węglowodanów został osiągnięty"})

    def protein_intake(self, request, weight):
        user_id = request.session.get('user_id')
        protein_intake = weight * 1.2

        try:
            consumption = Consumption.objects.get(user_id=user_id, date=date.today())
        except Consumption.DoesNotExist:
            return JsonResponse({
                                    'error': f'Brak danych dotyczących dzisiejszego spożycia dla użytkownika. Aby zbudować masę mięśniową musisz dostarczyć co najmniej {protein_intake}g białka'})

        protein = consumption.protein

        remaining_protein = protein_intake - protein
        if remaining_protein > 0:
            return JsonResponse({'message': f"Musisz zjeść dziś jeszcze {remaining_protein}g białka."})
        else:
            return JsonResponse({'message': "Dzienne zapotrzebowanie na białko zostało zapewnione"})


class SearchFoodView(View):
    def search_food(request):
        if request.method == 'GET':
            query = request.GET.get('query')  # Pobierz zapytanie wyszukiwania z parametru GET

            if query:  # Sprawdź, czy zapytanie nie jest puste
                # Wyszukaj jedzenie w bazie danych na podstawie zapytania
                foods = Food.objects.filter(name__icontains=query)
            else:
                foods = Food.objects.none()  # Jeśli zapytanie jest puste, zwróć pustą listę jedzenia

            return render(request, 'search_results.html', {'foods': foods, 'query': query})
        else:
            return render(request, 'search_results.html')  # Jeśli żądanie nie jest typu GET, zwróć pustą stronę

class ConsumptionView(View):
    def post(self, request):
        food_id = request.POST.get('food_id')
        amount = float(request.POST.get('amount'))
        food = Food.objects.get(pk=food_id)

        calories = (food.calories / 100) * amount
        fat = (food.fat / 100) * amount
        carbohydrates = (food.carbohydrates / 100) * amount
        protein = (food.protein / 100) * amount

        user_id = request.session.get('user_id')
        consumption = Consumption.objects.create(user_id=user_id, date=date.today(), calories=calories, fat=fat, carbohydrates=carbohydrates, protein=protein)

        return redirect('consumption_list')  # Przekierowanie na listę spożycia

class RemoveFromConsumptionView(View):
    def post(self, request):
        consumption_id = request.POST.get('consumption_id')
        Consumption = Consumption.objects.get(pk=consumption_id)
        consumption.delete()
        return redirect('consumption_list')

class RegisterUser(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()  # Zapisanie danych formularza do bazy danych
            return redirect('success')  # Przekierowanie na stronę potwierdzającą udaną rejestrację
        return render(request, 'register.html', {'form': form})

