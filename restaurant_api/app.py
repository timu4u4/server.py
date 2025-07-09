from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Datenbankverbindung herstellen
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Tabellen erstellen, wenn sie noch nicht existieren
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservationen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            uhrzeit TEXT NOT NULL,
            personen INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bestellungen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gericht TEXT NOT NULL,
            menge INTEGER NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Serverstart und DB-Initialisierung
init_db()

# Endpunkt für Reservierungen
@app.route('/reservierung', methods=['POST'])
def reservierung():
    data = request.json
    name = data.get('name')
    uhrzeit = data.get('uhrzeit')
    personen = data.get('personen')

    if not name or not uhrzeit or not personen:
        return jsonify({'error': 'Fehlende Daten'}), 400

    conn = get_db_connection()
    conn.execute('INSERT INTO reservationen (name, uhrzeit, personen) VALUES (?, ?, ?)',
                 (name, uhrzeit, personen))
    conn.commit()
    conn.close()

    return jsonify({'status': 'Reservierung gespeichert'})

# Endpunkt für Bestellungen
@app.route('/bestellung', methods=['POST'])
def bestellung():
    data = request.json
    name = data.get('name')
    gericht = data.get('gericht')
    menge = data.get('menge')

    if not name or not gericht or not menge:
        return jsonify({'error': 'Fehlende Daten'}), 400

    conn = get_db_connection()
    conn.execute('INSERT INTO bestellungen (name, gericht, menge) VALUES (?, ?, ?)',
                 (name, gericht, menge))
    conn.commit()
    conn.close()

    return jsonify({'status': 'Bestellung gespeichert'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

app.py