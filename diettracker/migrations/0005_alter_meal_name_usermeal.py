# Generated by Django 5.0.2 on 2024-03-01 11:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diettracker', '0004_consumption_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='meal',
            name='name',
            field=models.CharField(max_length=30),
        ),
        migrations.CreateModel(
            name='UserMeal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diettracker.meal')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'meal')},
            },
        ),
    ]
