# Generated by Django 5.0.2 on 2024-03-01 13:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diettracker', '0005_alter_meal_name_usermeal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meal',
            name='user',
        ),
    ]