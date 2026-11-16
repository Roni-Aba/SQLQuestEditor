# SQL Quest Editor

Der SQL Quest Editor ist ein Django-basiertes Tool zum Erstellen und Bearbeiten von Leveln für SQL Spell Quest.

## Projekt installieren und starten

Die [Startanleitung](docs/starten.md) zeigt die Einrichtung mit Python 3.11
für macOS, Linux und Windows. Sie installiert Django und die übrigen
Abhängigkeiten aus `backend/requirements.txt`.

## Prüfungen

Öffne ein Terminal im Projektordner mit aktivierter Python-Umgebung:

```bash
cd backend
python manage.py check
python manage.py test --verbosity 2
```

Der Startseiten-Test prüft, ob die Seite erreichbar ist und die Einstiege zum
Erstellen und Laden eines Spiels enthält. Er benötigt keine Datenbank.
GitHub Actions führt die Prüfungen bei Pushes und Pull Requests mit Python 3.11
aus. Die vorhandene GitLab-Pipeline führt dieselben Django-Prüfungen aus.


## Verständliche Projektdokumentation

Beginne mit [Wofür ist der Editor da?](docs/verstehen.md), dem
[Tutorial für dein erstes Level](docs/erstes-level.md) oder der
[FAQ: Wo ändere ich was im Code?](docs/code-faq.md).
Die [Dokumentationsstartseite](docs/README.md) führt durch Bedienung, Gegenstandsarten,
Architektur und Tests.

HTML-Vorschau aus dem Projektordner mit aktivierter Python-Umgebung:

```bash
python -m pip install -r requirements-docs.txt
python -m mkdocs serve -a 127.0.0.1:8001
```

Mit `python -m mkdocs build --strict` entsteht die statische Website in `site/`.
