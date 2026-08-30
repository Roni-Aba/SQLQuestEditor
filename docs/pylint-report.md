# Pylint-Bericht

Stand: 2026-08-26

## Ausführung

Geprüfter Bereich: `backend/editor`, `backend/config` und `backend/manage.py`.

```bash
cd backend
python -m pylint --rcfile=.pylintrc editor config manage.py
```

Für die Ausführung wurde eine temporäre, isolierte Umgebung mit Pylint 3.3.9
und pylint-django 2.6.1 verwendet. Die Projektdateien und
`backend/requirements.txt` wurden nicht verändert.

Pylint meldet insgesamt **64 Diagnosen**. Die in `.pylintrc` aktivierten
Meldungen für fehlende Modul-, Klassen- und Funktionsdocstrings, zu wenige
öffentliche Methoden sowie Importfehler wurden wie vorgesehen nicht bewertet.

> Hinweis: Pylint gab eine fatale `F5110`-Meldung zur Django-Settings-Option
> aus. Der direkte Import von `config.settings` in derselben Umgebung war
> erfolgreich. Diese eine Meldung wird daher als Plugin-/Konfigurationsproblem
> getrennt von den 63 Code-Befunden gezählt. Der ausgegebene Gesamtwert betrug
> wegen dieser fatalen Meldung `0.00/10` und ist nicht als belastbare
> Codequalitätskennzahl zu lesen.

## Übersicht nach Pylint-Kategorie

| Kategorie | Präfix | Anzahl | Einordnung |
| --- | --- | ---: | --- |
| Fatal | `F` | 1 | Pylint-/Django-Plugin-Konfiguration |
| Error | `E` | 1 | möglicher Laufzeitfehler |
| Warning | `W` | 7 | ungenutzte bzw. doppelte/überschriebene Importe |
| Convention | `C` | 25 | Stil, Benennung, Zeilenlänge und Importsortierung |
| Refactor | `R` | 30 | Komplexität und duplizierter Code |
| **Gesamt** |  | **64** |  |

## Detail nach Meldungstyp

| Code | Meldungstyp | Kategorie | Anzahl | Bedeutung |
| --- | --- | --- | ---: | --- |
| `F5110` | `django-settings-module-not-found` | Fatal | 1 | pylint-django konnte die konfigurierte Settings-Referenz nicht laden, obwohl der direkte Import funktioniert. |
| `E0606` | `possibly-used-before-assignment` | Error | 1 | `level_picture_path` könnte vor einer Zuweisung verwendet werden. |
| `W0611` | `unused-import` | Warning | 3 | Import wird nicht verwendet. |
| `W0621` | `redefined-outer-name` | Warning | 2 | `Path` wird in einer Funktion erneut definiert. |
| `W0404` | `reimported` | Warning | 2 | `Path` wird mehrfach importiert. |
| `C0411` | `wrong-import-order` | Convention | 12 | Standardbibliothek, Django und lokale Importe sind nicht in der erwarteten Reihenfolge. |
| `C0325` | `superfluous-parens` | Convention | 5 | Überflüssige Klammern nach einer Zuweisung. |
| `C0415` | `import-outside-toplevel` | Convention | 3 | Import innerhalb einer Funktion statt auf Modulebene. |
| `C0302` | `too-many-lines` | Convention | 2 | Modul überschreitet 1.000 Zeilen. |
| `C0103` | `invalid-name` | Convention | 1 | Modulname entspricht nicht dem snake_case-Schema. |
| `C0301` | `line-too-long` | Convention | 1 | Zeile überschreitet 120 Zeichen. |
| `C0410` | `multiple-imports` | Convention | 1 | Mehrere Imports in einer Zeile. |
| `R0801` | `duplicate-code` | Refactor | 16 | Wiederholte Codeblöcke zwischen `utils.py`, `views.py` und `sqlParser.py`. |
| `R0914` | `too-many-locals` | Refactor | 4 | Funktion hat mehr als 20 lokale Variablen. |
| `R0915` | `too-many-statements` | Refactor | 4 | Funktion hat mehr als 50 Anweisungen. |
| `R0912` | `too-many-branches` | Refactor | 4 | Funktion hat mehr als 12 Verzweigungen. |
| `R0911` | `too-many-return-statements` | Refactor | 2 | Funktion hat mehr als 6 Rückgabestellen. |

## Fundorte

| Datei | Diagnosen | Anzahl |
| --- | --- | ---: |
| `editor/views.py` | 1× `E0606`, 12× `C0411`, 1× `C0325`, 1× `C0302`, 1× `C0410`, 3× `R0914`, 3× `R0915`, 3× `R0912`, 1× `R0911` | 27 |
| `manage.py` | 16× `R0801`, 1× `C0415` | 17 |
| `editor/utils.py` | 2× `C0325`, 1× `C0302`, 2× `W0621`, 2× `W0404`, 2× `C0415`, 1× `R0914`, 1× `R0915`, 1× `R0911`, 1× `R0912` | 13 |
| `editor/sqlParser.py` | 2× `C0325`, 1× `C0103` | 3 |
| `editor/models.py` | 1× `W0611` | 1 |
| `editor/admin.py` | 1× `W0611` | 1 |
| `editor/tests.py` | 1× `W0611` | 1 |
| `editor/urls.py` | 1× `C0301` | 1 |
| Pylint-Konfiguration | 1× `F5110` | 1 |

## Konkrete Fehler und priorisierte Einordnung

1. **Potentieller Programmfehler:**
   `editor/views.py:1513` in `create_level51_view` verwendet
   `level_picture_path` möglicherweise vor der Zuweisung (`E0606`). Dieser
   Befund sollte zuerst geprüft werden.

2. **Pylint-/Django-Integration:**
   `F5110` verhindert eine sinnvolle Pylint-Score-Bewertung. Da
   `import config.settings` erfolgreich ist, sollte die Konfiguration bzw. die
   Kompatibilität von `pylint-django` separat geprüft werden.

3. **Größte Wartbarkeitsblöcke:**
   16 Befunde zu dupliziertem Code (`R0801`) sowie 13 Befunde zu
   Funktionskomplexität (`R0911`, `R0912`, `R0914`, `R0915`). Besonders
   betroffen sind `editor/views.py` und `editor/utils.py`.

4. **Niedrig priorisierte Aufräumarbeiten:**
   Importsortierung (12× `C0411`), ungenutzte Importe (3× `W0611`) und
   überflüssige Klammern (5× `C0325`) sind überwiegend mechanisch behebbar.

## Vollständige nicht-duplizierte Fundorte

- `F5110`: Pylint-Kommandozeile bzw. Konfiguration.
- `E0606`: `editor/views.py:1513` (`create_level51_view`).
- `W0611`: `editor/models.py:1`, `editor/admin.py:1`, `editor/tests.py:1`.
- `W0621`, `W0404`, `C0415`: jeweils `editor/utils.py:220` und
  `editor/utils.py:245` (`Path`); zusätzlich `C0415` in `manage.py:11`.
- `C0325`: `editor/utils.py:177`, `editor/utils.py:178`,
  `editor/sqlParser.py:53`, `editor/sqlParser.py:55`, `editor/views.py:806`.
- `C0302`: `editor/utils.py:1`, `editor/views.py:1`.
- `C0103`: `editor/sqlParser.py:1`.
- `C0301`: `editor/urls.py:33`.
- `C0410`: `editor/views.py:2`.
- `C0411`: `editor/views.py:2` bis `editor/views.py:9` (12 einzelne
  Importsortierungsbefunde).
- `R0914`: `editor/utils.py:3`, `editor/views.py:490`,
  `editor/views.py:1889`, `editor/views.py:2296`.
- `R0915`: `editor/utils.py:3`, `editor/views.py:490`,
  `editor/views.py:927`, `editor/views.py:1889`.
- `R0911`: `editor/utils.py:316`, `editor/views.py:490`.
- `R0912`: `editor/utils.py:804`, `editor/views.py:490`,
  `editor/views.py:927`, `editor/views.py:1889`.
- `R0801`: 16 Paare duplizierter Blöcke zwischen `editor/utils.py`,
  `editor/views.py` und `editor/sqlParser.py`; die einzelnen Paarungen wurden
  im Pylint-Textreport ausgegeben und sind in dieser Häufigkeit enthalten.
