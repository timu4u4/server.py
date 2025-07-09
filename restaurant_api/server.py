# Flask und notwendige Module importieren
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import sqlite3  # Für die Verbindung zur SQLite-Datenbank

# Flask-App erstellen
app = Flask(__name__)

# =====================
# Konfiguration für den Mailversand (diese Daten musst du anpassen!)
# =====================
app.config['MAIL_SERVER'] = 'smtp.example.com'  # SMTP-Server (z. B. smtp.gmail.com)
app.config['MAIL_PORT'] = 587                   # Port für TLS
app.config['MAIL_USE_TLS'] = True               # TLS aktivieren (sicherer Versand)
app.config['MAIL_USERNAME'] = 'timkoch273@gmail.com'   #Empfänger E-Mail-Adresse
app.config['MAIL_PASSWORD'] = 'adminChef$Bistro2025'    #passwort
app.config['MAIL_DEFAULT_SENDER'] = 'berlinbistro25@gmail.com'  # Absender der E-Mail

# Mail-Objekt mit den obigen Einstellungen initialisieren
mail = Mail(app)

# =====================
# Funktion zur Datenbankverbindung
# =====================
def get_db_connection():
    conn = sqlite3.connect('database.db')  # Verbindung zur Datenbankdatei
    conn.row_factory = sqlite3.Row         # Für bessere Handhabung von Datenbankzeilen
    return conn

# =====================
# Funktion zum Erstellen der Tabelle (falls sie noch nicht existiert)
# =====================
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabelle "bestellungen" mit den benötigten Spalten anlegen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bestellungen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

# Beim Start des Programms die Tabelle erstellen (nur falls sie nicht existiert)
init_db()

# =====================
# Route /bestellung: Diese wird aufgerufen, wenn eine Bestellung gesendet wird
# =====================
@app.route('/bestellung', methods=['POST'])
def bestellung():
    data = request.json  # Die gesendeten JSON-Daten auslesen

    # Einzelne Felder aus den gesendeten Daten holen
    name = data.get('name')
    gericht = data.get('gericht')
    menge = data.get('menge')
    email = data.get('email')
    adresse = data.get('adresse')
    zusatz = data.get('zusatz', '')  # Falls kein Zusatz angegeben ist, leerer Text

    # Überprüfen, ob alle Pflichtfelder ausgefüllt wurden
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
        # Falls ein Fehler beim E-Mail-Versand auftritt, Fehlermeldung zurückgeben
        return jsonify({'error': f'Fehler beim E-Mail-Versand: {str(e)}'}), 500

    # Wenn alles erfolgreich war, Erfolgsmeldung zurückgeben
    return jsonify({'status': 'Vielen Dank für Ihre Bestellung!'})

    # =====================
    # Startet den Flask-Webserver, wenn dieses Skript direkt ausgeführt wird
    # =====================
if __name__ == "__main__":
    app.run(debug=True)  # Im Debug-Modus starten (zeigt Fehler direkt im Browser)