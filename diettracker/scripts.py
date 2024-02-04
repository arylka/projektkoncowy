import sqlite3
import csv

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS your_table (
                    column1 TEXT
                    )''')

# Dodaj kolejne kolumny za pomocą ALTER TABLE
for i in range(2, 509):
    try:
        cursor.execute(f"ALTER TABLE your_table ADD COLUMN column{i} TEXT")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise

with open('C:/Users/pnowa/Downloads/openfoodfacts_export.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter='\t')
    next(reader)
    for row in reader:
        if len(row) < 508:
            continue  # Pomiń wiersz, jeśli ma mniej niż 508 kolumn
        placeholders = ', '.join(['?' for _ in range(508)])
        query = f"INSERT INTO your_table VALUES ({placeholders})"
        cursor.execute(query, row[:508])  # Wstaw tylko pierwsze 508 wartości z wiersza

conn.commit()
conn.close()