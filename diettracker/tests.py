import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User, AnonymousUser
from diettracker.models import WeightEntry, Diet, Meal, Consumption, Food
from diettracker.forms import LoginForm
from unittest.mock import MagicMock
import datetime
from datetime import date
from django.utils import timezone
from django.test import RequestFactory, TestCase
from diettracker.views import ConsumptionListView, MealEditView, MealDeleteView, MealListView, FoodView, HomeView
from diettracker.forms import EditMealForm, MealForm
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect


@pytest.mark.django_db
def test_home_view(client):
    response = client.get(reverse('index'))

    assert response.status_code == 200


@pytest.mark.django_db
def test_logout_view_redirects_to_login_page():
    username = 'testuser'
    password = 'testpassword'
    user = User.objects.create_user(username=username, password=password)

    client = Client()
    client.force_login(user)

    url = reverse('logout')
    response = client.get(url, follow=True)

    assert response.status_code == 200
    assert response.redirect_chain[-1][0] == reverse('login')

@pytest.mark.django_db
def test_logout_view_redirects_to_login_page_when_not_logged_in():
    client = Client()

    url = reverse('logout')
    response = client.get(url, follow=True)

    assert response.status_code == 200
    assert response.redirect_chain[-1][0] == reverse('login')

@pytest.mark.django_db
def test_weight_chart_view_redirects_to_login_page_when_not_logged_in():
    client = Client()
    url = reverse('weight_chart')
    response = client.get(url, follow=True)

    assert response.status_code == 404
    assert response.redirect_chain[-1][0] == f'/accounts/login/?next={url}'


@pytest.mark.django_db
def test_weight_chart_view_displays_chart_when_logged_in():
    user = User.objects.create_user(username='testuser', password='testpassword')

    weight_entry_mock = WeightEntry.objects.create(user=user, weight=70, date=date(2023, 1, 1))

    WeightEntry.objects.filter = MagicMock(return_value=[weight_entry_mock])

    client = Client()
    client.force_login(user)

    url = reverse('weight_chart')

    response = client.get(url)

    assert response.status_code == 200
    assert response.content


@pytest.mark.django_db
def test_success_view_returns_success_template():
    client = Client()
    response = client.get(reverse('success'))
    assert response.status_code == 200
    assert 'success.html' in [template.name for template in response.templates]


@pytest.mark.django_db
def test_profile_view_returns_profile_template():
    client = Client()
    response = client.get(reverse('profile'))

    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=/profile/'


@pytest.mark.django_db
def test_profile_view_unauthenticated_user(client):
    response = client.get(reverse('profile'))

    assert response.status_code == 302

@pytest.mark.django_db
def test_diet_view_returns_diets_template():
    client = Client()
    response = client.get(reverse('diets'))
    assert response.status_code == 200
    assert 'diets.html' in [template.name for template in response.templates]

@pytest.mark.django_db
def test_login_view_get_request():
    client = Client()
    response = client.get(reverse('login'))
    assert response.status_code == 200
    assert 'form' in response.context
    assert isinstance(response.context['form'], LoginForm)


@pytest.mark.django_db
def test_login_view_post_request_with_valid_data():
    client = Client()
    login_data = {'username': 'testuser', 'password': 'testpassword'}
    response = client.post(reverse('login'), login_data, follow=True)

    assert response.status_code == 200

@pytest.mark.django_db
def test_bmi_view_get_request():
    client = Client()
    response = client.get(reverse('bmi'))
    assert response.status_code == 200
    assert 'bmi.html' in [template.name for template in response.templates]
    assert 'form' in response.context
    assert response.context['form'].__class__.__name__ == 'BMICalculatorForm'

@pytest.mark.django_db
def test_bmi_view_context():
    client = Client()
    response = client.get(reverse('bmi'))
    assert 'form' in response.context
    assert response.context['form'].__class__.__name__ == 'BMICalculatorForm'

@pytest.mark.django_db
def test_register_view_get_request():
    client = Client()
    response = client.get(reverse('register'))
    assert response.status_code == 200
    assert 'register.html' in [template.name for template in response.templates]
    assert 'form' in response.context
    assert response.context['form'].__class__.__name__ == 'RegisterForm'


@pytest.mark.django_db
def test_register_view_post_request_valid_data():
    client = Client()
    data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    response = client.post(reverse('register'), data, follow=True)

    assert response.status_code == 200

@pytest.mark.django_db
def test_register_view_post_request_invalid_data():
    client = Client()
    data = {
        'username': '',  # Nieprawidłowa nazwa użytkownika
        'password': 'testpassword'
    }
    response = client.post(reverse('register'), data, follow=True)

    # Oczekujemy, że nie uda się zarejestrować użytkownika z nieprawidłowymi danymi
    assert response.status_code == 200
    assert b'errorlist' in response.content
@pytest.mark.django_db
def test_update_diet_view_get_request():
    client = Client()
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.force_login(user)

    response = client.get(reverse('update_diet'))

    assert response.status_code == 200
    assert 'update_diet.html' in [template.name for template in response.templates]
    assert 'form' in response.context
    assert response.context['form'].__class__.__name__ == 'DietForm'

@pytest.mark.django_db
def test_update_diet_view_post_request_valid_data():
    client = Client()
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.force_login(user)

    data = {
        'diet_type': 'Low Carb',
        'calories': 1800,
        'protein': 120,
        'carbohydrates': 150,
        'fat': 60,
    }

    response = client.post(reverse('update_diet'), data)

    assert response.status_code == 302
    assert response.url == reverse('success')
    assert Diet.objects.filter(user=user).exists()

@pytest.mark.django_db
def test_weight_update_view_get_request():
    client = Client()
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.force_login(user)

    response = client.get(reverse('update_weight'))

    assert response.status_code == 200
    assert 'update_weight.html' in [template.name for template in response.templates]
    assert 'form' in response.context
    assert response.context['form'].__class__.__name__ == 'WeightUpdateForm'


@pytest.mark.django_db
def test_weight_update_view_post_request_valid_data():
    client = Client()
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.force_login(user)

    today = datetime.date.today().strftime('%Y-%m-%d')

    data = {
        'weight': 70.0,
        'date': today,
    }

    response = client.post(reverse('update_weight'), data)

    assert response.status_code == 302
    assert response.url == reverse('success')

    try:
        WeightEntry.objects.get(user=user, weight=70.0, date=today)
    except WeightEntry.DoesNotExist:
        assert False, "WeightEntry does not exist for user {} with weight {} and date {}".format(user, 70.0, today)

@pytest.mark.django_db
def test_food_view_returns_food_template():
    client = Client()
    response = client.get(reverse('food'))
    assert response.status_code == 200
    assert 'food.html' in [template.name for template in response.templates]


@pytest.mark.django_db
def test_all_meals_view(client):
    client = Client()

    response = client.get(reverse('all_meals'))

    assert response.status_code == 200

    assert b'Wszystkie posi\xc5\x82ki' in response.content
    assert b'Wpisy s\xc4\x85 tworzone przez u\xc5\xbcytkownik\xc3\xb3w, wi\xc4\x99c warto\xc5\x9bci mog\xc4\x85 nie by\xc4\x87 dok\xc5\x82adne.' in response.content


@pytest.mark.django_db
def test_all_meals_view_for_authenticated_user(client):
    user = User.objects.create_user(username='testuser', password='testpassword')

    client.login(username='testuser', password='testpassword')

    meal1 = Meal.objects.create(user=user, name='Breakfast', calories=300, protein=10, carbohydrates=40, fat=10)
    meal2 = Meal.objects.create(user=user, name='Lunch', calories=500, protein=20, carbohydrates=60, fat=15)

    response = client.get(reverse('all_meals'))

    assert response.status_code == 200

    meals = response.context['meals']
    assert list(meals) == [meal1, meal2]

@pytest.mark.django_db
def test_consumption_list_view_post_authenticated_user():
    user = User.objects.create_user(username='testuser', password='testpassword')

    consumption = Consumption.objects.create(user=user, date=timezone.now().date(), calories=700, fat=30, carbohydrates=60, protein=20)

    request = RequestFactory().post(reverse('consumption_list'), {'delete_consumption': consumption.id})
    request.user = user

    response = ConsumptionListView.as_view()(request)

    assert response.status_code == 302
    assert response.url == reverse('consumption_list')


@pytest.mark.django_db
def test_access_consumption_list_view_authenticated_user():
    user = User.objects.create_user(username='testuser', password='testpassword')

    request = RequestFactory().get(reverse('consumption_list'))
    request.user = user

    response = ConsumptionListView.as_view()(request)

    assert response.status_code == 200

@pytest.mark.django_db
def test_consumption_list_view_anonymous_user():
    request = RequestFactory().get(reverse('consumption_list'))
    request.user = AnonymousUser()

    view = ConsumptionListView.as_view()

    response = view(request)

    assert response.status_code == 302
    assert response.url == reverse('login')



@pytest.mark.django_db
def test_meal_edit_view_authenticated_user():
    user = User.objects.create_user(username='testuser', password='testpassword')

    meal = Meal.objects.create(user=user, name='Test Meal', calories=500)

    request = RequestFactory().get(reverse('meal_edit', kwargs={'pk': meal.pk}))
    request.user = user

    response = MealEditView.as_view()(request, pk=meal.pk)

    assert response.status_code == 200

@pytest.mark.django_db
def test_meal_edit_view_negative_calories():
    user = User.objects.create_user(username='testuser', password='testpassword')

    meal = Meal.objects.create(user=user, name='Test Meal', calories=-500)

    request = RequestFactory().get(reverse('meal_edit', kwargs={'pk': meal.pk}))
    request.user = user

    response = MealEditView.as_view()(request, pk=meal.pk)

    assert response.status_code == 200

@pytest.mark.django_db
def test_home_view_user(client):
    response = client.get(reverse('index'))

    assert response.status_code == 200

@pytest.mark.django_db
def test_meal_edit_view(client):
    user = User.objects.create_user(username='testuser', password='testpassword')

    client.login(username='testuser', password='testpassword')

    meal = Meal.objects.create(name='Test Meal', calories=500, protein=20, carbohydrates=50, fat=10, user=user)

    updated_name = 'Updated Meal'
    updated_calories = 600

    data = {
        'name': updated_name,
        'calories': updated_calories,
        'protein': meal.protein,
        'carbohydrates': meal.carbohydrates,
        'fat': meal.fat,
    }

    response = client.post(reverse('meal_edit', kwargs={'pk': meal.pk}), data)

    assert response.status_code == 302

    updated_meal = Meal.objects.get(pk=meal.pk)

    assert updated_meal.name == updated_name
    assert updated_meal.calories == updated_calories

@pytest.mark.django_db
def test_meal_delete_view_authenticated_user():
    user = User.objects.create_user(username='testuser', password='testpassword')

    meal = Meal.objects.create(user=user, name='Test Meal', calories=500)

    request = RequestFactory().post(reverse('meal_delete', kwargs={'pk': meal.pk}))
    request.user = user

    response = MealDeleteView.as_view()(request, pk=meal.pk)

    assert response.status_code == 302


@pytest.mark.django_db
def test_meal_delete_view_unauthenticated_user(client):
    # Utwórz użytkownika
    user = User.objects.create_user(username='testuser', password='testpassword')

    # Utwórz instancję posiłku dla użytkownika
    meal = Meal.objects.create(user=user, name='Test Meal', calories=500)

    # Utwórz żądanie DELETE
    url = reverse('meal_delete', kwargs={'pk': meal.pk})
    response = client.delete(url)

    assert response.status_code == 302

@pytest.mark.django_db
def test_food_view():
    client = Client()
    response = client.get(reverse('food'))
    assert response.status_code == 200
@pytest.mark.django_db
def test_meal_list_view_post_authenticated_user():
    user = User.objects.create_user(username='testuser', password='testpassword')

    request = RequestFactory().post(reverse('meal_list'), data={
        'name': 'Test Meal',
        'calories': 500,
        'protein': 30,
        'carbohydrates': 50,
        'fat': 20
    })
    request.user = user

    response = MealListView.as_view()(request)

    assert response.status_code == 302

    last_meal = Meal.objects.filter(user=user).last()

    assert last_meal.name == 'Test Meal'
    assert last_meal.calories == 500
    assert last_meal.protein == 30
    assert last_meal.carbohydrates == 50
    assert last_meal.fat == 20

@pytest.mark.django_db
def test_meal_list_view_post_authenticated_user_invalid_data():
    user = User.objects.create_user(username='testuser', password='testpassword')

    request = RequestFactory().post(reverse('meal_list'), data={
        'name': 'Test Meal',
        'calories': 6000,
        'protein': 1000,
        'carbohydrates': 1000,
        'fat': 1000
    })
    request.user = user

    response = MealListView.as_view()(request)

    assert response.status_code == 400


@pytest.mark.django_db
def test_meal_list_view_post_authenticated_user_missing_data():
    user = User.objects.create_user(username='testuser', password='testpassword')

    request = RequestFactory().post(reverse('meal_list'), data={
        'name': 'Test Meal',
    })
    request.user = user

    response = MealListView.as_view()(request)

    assert response.status_code == 400


