from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from diettracker.models import Diet, WeightEntry, Food, Meal, UserMeal
from django.contrib.auth.models import User
from datetime import date

class LoginForm(forms.Form):
    username = forms.CharField(label='Nazwa użytkownika')
    password = forms.CharField(label='Hasło', widget=forms.PasswordInput)

class RegisterForm(forms.ModelForm):
    password = forms.CharField(max_length=50, label='Hasło', widget=forms.PasswordInput)
    re_password = forms.CharField(max_length=50, label='Powtórz hasło', widget=forms.PasswordInput)
    username = forms.CharField(max_length=150, label='Nazwa użytkownika')
    class Meta:
        model = User
        fields = ['username',]

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('re_password')
        if p1 is None or p2 is None or p1 != p2:
            raise ValidationError('Hasła muszą być identyczne')
        return cleaned_data


from django import forms


class DietForm(forms.ModelForm):
    min_calories = forms.IntegerField(label='Minimalna liczba kalorii', required=False)
    max_calories = forms.IntegerField(label='Maksymalna liczba kalorii', required=False)
    max_fat = forms.IntegerField(label='', required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'hidden': True}))
    max_protein = forms.IntegerField(label='', required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'hidden': True}))
    min_protein = forms.IntegerField(label='Minimalna ilość białka (w gramach)', required=False)
    max_carbohydrates = forms.IntegerField(label='Maksymalna ilość węglowodanów (w gramach)', required=False)

    def clean(self):
        cleaned_data = super().clean()
        min_calories = cleaned_data.get('min_calories')
        max_calories = cleaned_data.get('max_calories')
        min_protein = cleaned_data.get('min_protein')
        max_protein = cleaned_data.get('max_protein')

        if min_calories is not None and max_calories is not None:
            if min_calories >= max_calories:
                raise forms.ValidationError('Minimalna liczba kalorii musi być mniejsza niż maksymalna liczba kalorii')

        if min_protein is not None and max_protein is not None:
            if min_protein >= max_protein:
                raise forms.ValidationError('Minimalna ilość białka musi być mniejsza niż maksymalna ilość białka')

    class Meta:
        model = Diet
        fields = ['min_calories', 'max_calories', 'max_fat', 'max_protein', 'min_protein', 'max_carbohydrates']
        labels = {
            'max_fat': 'Maksymalna ilość tłuszczu (w gramach)',
            'max_carbohydrates': 'Maksymalna ilość węglowodanów (w gramach)',
        }
        widgets = {
            'min_calories': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_calories': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_fat': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_protein': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_protein': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_carbohydrates': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class WeightUpdateForm(forms.ModelForm):
    weight = forms.DecimalField(max_digits=4, decimal_places=1)

    class Meta:
        model = WeightEntry
        fields = ['weight',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['weight'].label = "Aktualna waga"

    def clean(self):
        cleaned_data = super().clean()
        weight = cleaned_data.get('weight')
        if weight <= 0:
            raise forms.ValidationError("Waga musi być większa od zera.")
        if weight >= 500:
            raise forms.ValidationError("Waga jest za wysoka. Upewnij się że dane są poprawne!")
        return cleaned_data

    def save(self, user, commit=True):
        existing_entry = WeightEntry.objects.filter(user=user, date=date.today()).first()
        if existing_entry:
            existing_entry.weight = self.cleaned_data['weight']
            existing_entry.save()
            return existing_entry
        else:
            instance = super().save(commit=False)
            instance.user = user
            instance.date = date.today()
            if commit:
                instance.save()
            return instance

class BMICalculatorForm(forms.Form):
    weight = forms.DecimalField(label='Waga (kg)', min_value=0)
    height = forms.DecimalField(label='Wzrost (cm)', min_value=0)

    def clean(self):
        cleaned_data = super().clean()
        weight = cleaned_data.get('weight')
        height = cleaned_data.get('height')

        if weight is None or height is None:
            raise forms.ValidationError("Wprowadź poprawne wartości dla wagi i wzrostu.")

        if weight <= 0 or height <= 0:
            raise forms.ValidationError("Waga i wzrost muszą być większe od zera.")

        return cleaned_data


class ConsumptionForm(forms.Form):
    food = forms.ModelChoiceField(queryset=Food.objects.all(), empty_label="Wybierz produkt", label="Jedzenie")
    amount = forms.FloatField(label="Ilość (w gramach)")


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['name', 'calories', 'protein', 'carbohydrates', 'fat']
        labels = {
            'name': 'Nazwa',
            'calories': 'Kalorie',
            'protein': 'Białko',
            'carbohydrates': 'Węglowodany',
            'fat': 'Tłuszcze',
        }
        widgets = {
            'protein': forms.NumberInput(attrs={'placeholder': ''}),
            'carbohydrates': forms.NumberInput(attrs={'placeholder': ''}),
            'fat': forms.NumberInput(attrs={'placeholder': ''}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['calories'].required = True

class EditMealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['name', 'calories', 'protein', 'carbohydrates', 'fat']
        labels = {
            'name': 'Nazwa',
            'calories': 'Kalorie',
            'protein': 'Białko',
            'carbohydrates': 'Węglowodany',
            'fat': 'Tłuszcze',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nazwa'}),
            'calories': forms.NumberInput(attrs={'placeholder': 'Kcal'}),
            'protein': forms.NumberInput(attrs={'placeholder': 'Białko'}),
            'carbohydrates': forms.NumberInput(attrs={'placeholder': 'Węglowodany'}),
            'fat': forms.NumberInput(attrs={'placeholder': 'Tłuszcze'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.error_messages = {'required': 'To pole jest wymagane.'}
        if self.instance:
            self.fields['name'].widget.attrs['placeholder'] = self.instance.name
            if self.instance.calories is not None:
                self.fields['calories'].widget.attrs['placeholder'] = str(self.instance.calories)
            if self.instance.protein is not None:
                self.fields['protein'].widget.attrs['placeholder'] = str(self.instance.protein)
            if self.instance.carbohydrates is not None:
                self.fields['carbohydrates'].widget.attrs['placeholder'] = str(self.instance.carbohydrates)
            if self.instance.fat is not None:
                self.fields['fat'].widget.attrs['placeholder'] = str(self.instance.fat)
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class MealConsumptionForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super(MealConsumptionForm, self).__init__(*args, **kwargs)
        if user:
            user_meals = UserMeal.objects.filter(user=user).values_list('meal', flat=True)
            self.fields['meal'].queryset = Meal.objects.filter(models.Q(user=user) | models.Q(pk__in=user_meals))

    meal = forms.ModelChoiceField(queryset=Meal.objects.none(), label="Posiłek")

class AddMealForm(forms.Form):
    meal_id = forms.IntegerField(widget=forms.HiddenInput())

    def clean_meal_id(self):
        meal_id = self.cleaned_data.get('meal_id')
        try:
            meal = Meal.objects.get(pk=meal_id)
        except Meal.DoesNotExist:
            raise forms.ValidationError("Nieprawidłowy identyfikator posiłku.")
        return meal_id
