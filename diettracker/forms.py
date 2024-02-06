from django import forms
from diettracker.models import User

class LoginForm(forms.Form):
    username = forms.CharField(label='Nazwa użytkownika')
    password = forms.CharField(label='Hasło', widget=forms.PasswordInput)


class RegisterForm(forms.ModelForm):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]

    name = forms.CharField(label='Nazwa użytkownika', max_length=20, required=True)
    sex = forms.ChoiceField(label='Płeć', choices=SEX_CHOICES, required=True)
    height = forms.FloatField(label='Wzrost w centymetrach', required=True)
    weight = forms.FloatField(label='Waga w kilogramach', required=True, )
    date_of_birth = forms.DateField(label='Data urodzenia', widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = User
        fields = ['name', 'sex', 'height', 'date_of_birth', 'diet']