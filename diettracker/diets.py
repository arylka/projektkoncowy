from diettracker.models import Diet

def dodaj_przykladowa_dieta():
    dieta = Diet(
        name="Przykładowa dieta",
        min_calories=2000,
        max_calories=2500,
        max_fat=70,
        max_protein=120,
        max_carbohydrates=300
    )
    dieta.save()

# Wywołanie funkcji dodającej przykładową dietę do bazy danych
dodaj_przykladowa_dieta()