
from flask import Flask, jsonify, request, render_template
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("vehicles.db")

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS owners (
            owner_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT
        );

        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT NOT NULL UNIQUE,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER,
            color TEXT,
            engine_volume REAL,
            owner_id INTEGER NOT NULL,
            FOREIGN KEY(owner_id)
            REFERENCES owners(owner_id)
        );

        CREATE TABLE IF NOT EXISTS technical_inspections (
            inspection_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            inspection_date TEXT NOT NULL,
            next_inspection_date TEXT,
            result TEXT NOT NULL,
            FOREIGN KEY(vehicle_id)
            REFERENCES vehicles(vehicle_id)
        );
        """)

        # Бастапқы иелер
        if con.execute("SELECT COUNT(*) FROM owners").fetchone()[0] == 0:
            owners = [
                ("Айдос Нұрланов", "+7 701 123 45 67", "aidos@mail.com"),
                ("Әлия Сәрсенова", "+7 702 234 56 78", "aliya@mail.com"),
                ("Ержан Қасымов", "+7 705 345 67 89", "erzhan@mail.com"),
                ("Дана Мұратова", "+7 707 111 22 33", "dana@mail.com"),
                ("Нұрсұлтан Әлиев", "+7 747 222 33 44", "nursultan@mail.com")
            ]

            con.executemany("""
                INSERT INTO owners(full_name, phone, email)
                VALUES (?, ?, ?)
            """, owners)

            # Көліктер
            cars = [
                ("123ABC01", "Toyota", "Camry", 2022, "Күміс", 2.5, 1),
                ("456DEF02", "Hyundai", "Tucson", 2021, "Қара", 2.0, 2),
                ("789GHI01", "Kia", "Sportage", 2023, "Сұр", 2.0, 1),
                ("321JKL02", "Chevrolet", "Cobalt", 2020, "Ақ", 1.5, 3),
                ("654MNO01", "Toyota", "Corolla", 2024, "Көк", 1.8, 3),
                ("111AAA02", "BMW", "530i", 2022, "Қара", 2.0, 4),
                ("222BBB02", "Mercedes-Benz", "E200", 2021, "Ақ", 2.0, 5)
            ]

            con.executemany("""
                INSERT INTO vehicles
                (plate_number, brand, model, year, color,
                 engine_volume, owner_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, cars)

            # Техникалық байқау
            inspections = [
                (1, "2026-01-10", "2027-01-10", "Өтті"),
                (2, "2026-02-12", "2027-02-12", "Өтті"),
                (3, "2026-03-14", "2027-03-14", "Өтті"),
                (4, "2026-04-16", "2027-04-16", "Өтпеді"),
                (5, "2026-05-18", "2027-05-18", "Өтті")
            ]

            con.executemany("""
                INSERT INTO technical_inspections
                (vehicle_id, inspection_date,
                 next_inspection_date, result)
                VALUES (?, ?, ?, ?)
            """, inspections)


def get_data():
    with connect() as con:
        owners = [
            dict(r) for r in
            con.execute("SELECT * FROM owners")
        ]

        vehicles = [
            dict(r) for r in
            con.execute("SELECT * FROM vehicles")
        ]

        inspections = [
            dict(r) for r in
            con.execute("SELECT * FROM technical_inspections")
        ]

    return {
        "owners": owners,
        "vehicles": vehicles,
        "inspections": inspections
    }

@app.route("/")
def home():
    return render_template("index.html")



@app.route("/api/data", methods=["GET"])
def data_api():
    return jsonify(get_data())

@app.route("/api/reports")
def reports():
    with connect() as con:

        brands = [
            dict(r) for r in con.execute("""
                SELECT brand, COUNT(*) AS total
                FROM vehicles
                GROUP BY brand
                ORDER BY total DESC
            """)
        ]

        results = [
            dict(r) for r in con.execute("""
                SELECT result, COUNT(*) AS total
                FROM technical_inspections
                GROUP BY result
            """)
        ]

    return jsonify({
        "brands": brands,
        "inspections": results
    })




init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
