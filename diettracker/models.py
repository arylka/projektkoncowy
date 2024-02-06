from django.db import models
import datetime
from django.contrib.auth.models import User

# Create your models here.

class Diet(models.Model):
    """
    Model ten służy do przechowywania spersonalizowanych zaleceń odżywiania użytkownika
    """
    name = models.CharField(max_length=100)
    min_calories = models.PositiveIntegerField(blank=True, null=True)
    max_calories = models.PositiveIntegerField(blank=True, null=True)
    max_fat = models.PositiveIntegerField(blank=True, null=True)
    max_protein = models.PositiveIntegerField(blank=True, null=True)
    max_carbohydrates = models.PositiveIntegerField(blank=True, null=True)

class User(models.Model):
    """
    Model reprezentujący użytkownika.
    """
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    name = models.CharField(max_length=20)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    height = models.FloatField()
    weight = models.FloatField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_of_birth = models.DateField(default='2000-01-01')
    diet = models.ForeignKey(Diet, on_delete=models.SET_NULL, blank=True, null=True)
class Food(models.Model):
    """
    Model reprezentujący produkt spożywczy.
    """
    name = models.CharField(max_length=100)
    calories = models.FloatField()
    protein = models.FloatField()
    carbohydrates = models.FloatField()
    fat = models.FloatField()


class Meal(models.Model):
    """
    Model reprezentujący posiłek.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    foods = models.ManyToManyField(Food)

class WeightEntry(models.Model):
    """
    Model ten służy do przechowywania wpisów użytkowników dotyczących ich wagi
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.FloatField()
    date = models.DateField()

    class Meta:
        unique_together = ('user', 'date')


class Consumption(models.Model):
    """
    Model ten służy do przechowywania informacji nt ilości kalorii i makroskładników spożytych przez użytkownika danego dnia
    """
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    date = models.DateField()
    calories = models.PositiveIntegerField()
    fat = models.PositiveIntegerField()
    carbohydrates = models.PositiveIntegerField()
    protein = models.PositiveIntegerField()

