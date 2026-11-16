# HTML und Django verstehen

## Was ist ein Django-Template?

Eine HTML-Vorlage mit Platzhaltern und Anweisungen. Django setzt die Daten ein,
bevor die Seite an den Browser geht. Der Browser bekommt fertiges HTML.

```html
<h1>{{ saved_level.id }}</h1>
```

`{{ saved_level.id }}` zeigt die ID aus dem Kontext, den die View übergeben hat.

## Wie wird eine vorhandene Basis verwendet?

```html
{% extends "editor/base.html" %}
{% block content %}
  <h1>Mein Inhalt</h1>
{% endblock %}
```

`base.html` enthält das gemeinsame Grundgerüst. Eine wiederverwendbare
Formularsektion kann über `{% include %}` eingebunden werden.

## Wie binde ich ein vorhandenes Bild oder JavaScript ein?

```html
{% load static %}
<img src="{% static 'editor/img/cat1.png' %}" alt="Cosmo">
<script src="{% static 'editor/js/start.js' %}" defer></script>
```

Die Beispiele zeigen die Syntax. Lade `start.js` nur auf einer Seite, die die
passenden Formularfelder besitzt. Statische Dateien liegen unter `static/`,
HTML-Vorlagen unter `templates/`.

## Warum steht im Formular ein URL-Name?

```html
<form method="post" action="{% url 'create_level2' %}">
  {% csrf_token %}
  <!-- Hier stehen die Formulareingaben. -->
  <button type="submit">Weiter</button>
</form>
```

Django löst `create_level2` über `urls.py` auf. Der CSRF-Token gehört zu
POST-Formularen. Feldnamen verbinden die Eingabe mit `request.POST` in Python.

## Darf ich vorhandene CSS-Dateien erweitern?

Beachte `AGENTS.md`: Neue Oberflächen verwenden Bootstrap-Klassen. Der vorhandene
CSS-Bestand ist kein allgemeiner Erweiterungspunkt. Bei Figma-Aufgaben gelten
zusätzlich die Regeln für neue Templates und reine Render-Views.

[Zurück zur Code-FAQ](../code-faq.md)
