import sqlite3
import csv

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS cleandata (
                    column1 TEXT,
                    column32 TEXT,
                    column77 TEXT,
                    column78 TEXT,
                    column149 TEXT,
                    column172 TEXT,
                    column173 TEXT,
                    column178 TEXT,
                    column182 TEXT,
                    column190 TEXT,
                    column202 TEXT
                    )''')

with open('C:/Users/pnowa/Downloads/openfoodfacts_export.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter='\t')
    next(reader)  # Pominięcie nagłówka, jeśli istnieje
    for row in reader:
        if len(row) < 203:  # Sprawdź, czy wiersz ma wystarczającą liczbę kolumn
            continue  # Pomiń wiersz, jeśli ma mniej niż 203 kolumny
        selected_columns = [row[i] for i in [0, 31, 76, 77, 148, 171, 172, 177, 181, 189, 201]]  # Wybierz tylko określone kolumny
        cursor.execute("INSERT INTO cleandata VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", selected_columns)

conn.commit()
conn.close()