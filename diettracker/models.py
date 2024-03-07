from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models
import datetime

# Create your models here.

class Diet(models.Model):
    """
    Model ten służy do przechowywania spersonalizowanych zaleceń odżywiania użytkownika
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    min_calories = models.PositiveIntegerField(blank=True, null=True)
    max_calories = models.PositiveIntegerField(blank=True, null=True)
    max_fat = models.PositiveIntegerField(blank=True, null=True)
    max_protein = models.PositiveIntegerField(blank=True, null=True)
    min_protein = models.PositiveIntegerField(blank=True, null=True)
    max_carbohydrates = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        app_label = 'diettracker'


class Food(models.Model):
    """
    Model reprezentujący produkt spożywczy.
    """
    name = models.CharField(max_length=100)
    calories = models.FloatField()
    protein = models.FloatField()
    carbohydrates = models.FloatField()
    fat = models.FloatField()

    class Meta:
        app_label = 'diettracker'

    def __str__(self):
        return self.name


class WeightEntry(models.Model):
    """
    Model ten służy do przechowywania wpisów użytkowników dotyczących ich wagi
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.FloatField()
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        app_label = 'diettracker'


class Consumption(models.Model):
    """
    Model ten służy do przechowywania informacji nt ilości kalorii i makroskładników spożytych przez użytkownika danego dnia
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="not available")
    date = models.DateField()
    calories = models.PositiveIntegerField()
    fat = models.PositiveIntegerField()
    carbohydrates = models.PositiveIntegerField()
    protein = models.PositiveIntegerField()

    class Meta:
        app_label = 'diettracker'

class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=30)
    calories = models.FloatField()
    protein = models.FloatField(blank=True, null=True)
    carbohydrates = models.FloatField(blank=True, null=True)
    fat = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def is_added_by_user(self, user):
        return UserMeal.objects.filter(user=user, meal=self).exists()

class UserMeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'meal')