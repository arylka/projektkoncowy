# Generated by Django 5.0.2 on 2024-02-27 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diettracker', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('calories_per_hour', models.FloatField()),
            ],
        ),
        migrations.DeleteModel(
            name='Meal',
        ),
    ]