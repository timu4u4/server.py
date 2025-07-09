# =====================
# Benötigte Module importieren
# =====================

from flask import Flask, request, jsonify          # Flask für Webserver, Request für Datenempfang, JSON für Antworten
from flask_mail import Mail, Message               # Für den Versand von E-Mails
from flask_cors import CORS                        # Für die Kommunikation mit externen Websites (z. B. deiner WordPress-Seite)
import sqlite3                                      # SQLite für lokale Datenbank

# =====================
# Flask-Anwendung erstellen
# =====================

app = Flask(__name__)
CORS(app)  # CORS aktivieren → erlaubt Anfragen von anderen Domains (z. B. WordPress-Website)

# =====================
# Konfiguration für den Mailversand
# =====================

app.config['MAIL_SERVER'] = 'smtp.gmail.com'          # SMTP-Server des Mail-Anbieters 
app.config['MAIL_PORT'] = 587                         # Typischer Port für TLS (verschlüsselter Versand)
app.config['MAIL_USE_TLS'] = True                     # TLS aktivieren
app.config['MAIL_USERNAME'] = 'timkoch273@gmail.com'  # E-Mail-Adresse des Absenders (Benutzername für SMTP)
app.config['MAIL_PASSWORD'] = 'kcfs usxh qvwj pzca'  # Passwort oder App-spezifisches Passwort (wenn 2FA aktiv ist)
app.config['MAIL_DEFAULT_SENDER'] = 'timkoch273@gmail.com'  # Absender, der in der E-Mail angezeigt wird

mail = Mail(app)  # Flask-Mail initialisieren

# =====================
# Funktion: Verbindung zur SQLite-Datenbank herstellen
# =====================

def get_db_connection():
    conn = sqlite3.connect('database.db')  # Verbindet sich mit der Datenbankdatei (automatisch angelegt, wenn nicht vorhanden)
    conn.row_factory = sqlite3.Row         # Option für bessere Handhabung von Abfrageergebnissen
    return conn

# =====================
# Funktion: Tabelle "bestellungen" erstellen (wenn sie noch nicht existiert)
# =====================

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL-Befehl zum Anlegen der Tabelle mit allen benötigten Spalten
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bestellungen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Automatisch generierte ID
            name TEXT,
            gericht TEXT,
            menge INTEGER,
            email TEXT,
            adresse TEXT,
            zusatz TEXT
        )
    ''')

    conn.commit()  # Änderungen speichern
    conn.close()   # Verbindung schließen

# Beim Start des Servers wird die Tabelle automatisch angelegt (falls nötig)
init_db()

# =====================
# API-Endpunkt: POST-Anfragen an /bestellung entgegennehmen
# =====================

@app.route('/bestellung', methods=['POST'])
def bestellung():
    data = request.json  # Die JSON-Daten, die von der Website gesendet wurden

    # Einzelne Werte aus dem JSON extrahieren
    name = data.get('name')
    gericht = data.get('gericht')
    menge = data.get('menge')
    email = data.get('email')
    adresse = data.get('adresse')
    zusatz = data.get('zusatz', '')  # Optionales Feld, Standardwert: leer

    # Überprüfung: Alle Pflichtfelder müssen ausgefüllt sein
    if not name or not gericht or not menge or not email or not adresse:
        return jsonify({'error': 'Bitte alle Pflichtfelder ausfüllen.'}), 400

    # =====================
    # Daten in die Datenbank einfügen
    # =====================
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO bestellungen (name, gericht, menge, email, adresse, zusatz)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, gericht, menge, email, adresse, zusatz))
    conn.commit()
    conn.close()

    # =====================
    # Bestätigungs-E-Mail versenden
    # =====================
    try:
        # Neue E-Mail-Nachricht vorbereiten
        msg = Message("Ihre Bestellung bei unserem Restaurant", recipients=[email])
        msg.body = f"""Hallo {name},

vielen Dank für Ihre Bestellung!

Bestellübersicht:
- Gericht: {gericht}
- Menge: {menge}
- Adresse: {adresse}
- Zusatzinfo: {zusatz or '—'}

Wir melden uns bald bei Ihnen.

Ihr Restaurant-Team
"""
        mail.send(msg)  # E-Mail absenden
    except Exception as e:
        # Fehler beim E-Mail-Versand melden
        return jsonify({'error': f'Fehler beim E-Mail-Versand: {str(e)}'}), 500

    # Erfolgsantwort zurückgeben
    return jsonify({'status': 'Vielen Dank für Ihre Bestellung!'})

# =====================
# Lokalen Entwicklungsserver starten (wird bei Render ignoriert)
# =====================

if __name__ == "__main__":
    app.run(debug=True)
