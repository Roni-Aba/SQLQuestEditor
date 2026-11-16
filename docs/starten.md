# Projekt starten

## Was brauche ich?

Du brauchst den Projektordner und Python. Die automatischen Projektprüfungen
verwenden Python 3.11. Verwende dieselbe Version für die lokale Einrichtung.
Ein Node-/npm-Build ist für den Editor nicht nötig.

## Wie richte ich die Python-Umgebung ein?

Öffne ein Terminal im Projektordner, in dem `mkdocs.yml` liegt. Erstelle und
aktiviere die Umgebung für dein Betriebssystem.

**macOS oder Linux**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Wenn du später ein neues Terminal öffnest, aktiviere die vorhandene Umgebung
erneut. Der Befehl `python --version` zeigt dir, welche Python-Version du gerade
verwendest.

## Wie installiere ich die Abhängigkeiten und starte den Editor?

Führe mit aktivierter Umgebung dieselben Befehle unter macOS, Linux oder Windows
aus. Beginne im Projektordner:

```bash
python -m pip install -r backend/requirements.txt
cd backend
python manage.py migrate
python manage.py check
python manage.py runserver
```

`migrate` richtet die lokale Django-Datenbank ein. Öffne anschließend
<http://127.0.0.1:8000/>. Das Terminal mit dem Server bleibt offen.
Mit `Ctrl+C` beendest du den Server.

## Was bedeuten die Befehle?

| Befehl | Bedeutung |
|---|---|
| `venv` | Erstellt eine eigene Python-Umgebung für dieses Projekt |
| `pip install -r …` | Installiert die festgelegten Abhängigkeiten |
| `manage.py check` | Prüft die Django-Konfiguration |
| `manage.py runserver` | Startet den lokalen Entwicklungsserver |

## Wie starte ich nur die Dokumentation?

Im Projektordner, mit aktivierter Python-Umgebung:

```bash
python -m pip install -r requirements-docs.txt
python -m mkdocs serve
```

Öffne die Adresse aus dem Terminal. Django und MkDocs verwenden standardmäßig
beide Port 8000. Wenn Django bereits läuft, verwende:

```bash
python -m mkdocs serve -a 127.0.0.1:8001
```

## Wie erzeuge ich HTML-Dateien?

```bash
python -m mkdocs build --strict
```

Die Website entsteht im Ordner `site/`. Zum lokalen Anschauen inklusive Suche:

```bash
python -m http.server 8001 --directory site
```

Öffne <http://127.0.0.1:8001/>. Eine Veröffentlichung ist ein separater Schritt.
