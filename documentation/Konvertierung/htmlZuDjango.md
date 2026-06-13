# Von normalem HTML zu Django-HTML

## 1. Was ist der Unterschied?

Normales HTML sieht zum Beispiel so aus:

```html
<link rel="stylesheet" href="tableItem.css">
```
Der Browser sucht die tableItem.css direkt neben der HTML-File

In Django läuft das anders

Django trennt zwischen:
- Templates = HTML-Dateien
- Static Files = CSS, Bilder, Javascript, Font


## 2. Django Ordnerstruktur
```text
backend/
├── editor/
│   ├── templates/
│   │   └── editor/
│   │       └── start.html
│   │
│   └── static/
│       └── editor/
│           └── components/
│               └── tableItem/
│                   └── tableItem.css
```
## 3. HTML -> Django-HTML
In normalen HTML steht:
```
<link rel="stylesheet" href="tableItem.css">
```

In Django schreibt man 
```
<link rel="stylesheet" href="{% static 'editor/components/tableItem/tableItem.css' %}">
```

Damit Django nun {% static %} versteht, muss ganz oben im Template folgendes stehen
```
{% load static %}
```

## 4. Merksatz
HTML beschreibt Struktur
CSS Design
Django-Templates sind HTML-Files mit Django Syntax


## 5. Regeln für CSS-Files
Normales HTML
```
<link rel="stylesheet" href="style.css">
```
Django:
```
{% load static %}
<link rel="stylesheet" href="{% static 'appname/pfad/style.css' %}>
```

Beispiel
```
{% load static %}
<link rel="stylesheet" href="{% static 'editor/components/tableItem/tableItem.css' %}">
```

## 6. Regeln für Bilder

Normales HTML: 
```
<img src="images/logo.png">
```

Django:
```
<img src="{%static 'editor/js/script.js' %}"></script>
```

