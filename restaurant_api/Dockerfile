# Verwende ein offizielles Python-Image
FROM python:3.10-slim

# Setze das Arbeitsverzeichnis
WORKDIR /app

# Kopiere alle Dateien ins Container-Dateisystem
COPY . /app

# Installiere Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Starte die App
CMD ["python", "server.py"]
