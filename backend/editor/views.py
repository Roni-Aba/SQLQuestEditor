import json
from pathlib import Path
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect, render

def get_steps(active_step):
    steps = []
    for number in range(0, 9):
        steps.append({"number": number,"active": number <= active_step})
    return steps

def start_page(request):
    return render(request, "editor/start.html")

def level_view(request):
    game_file = Path(settings.BASE_DIR) / "SQLSpellQuest.json"
    name_of_levels = []
    if game_file.exists():
        with open(game_file, "r", encoding="utf-8") as file:
            game = json.load(file)
        for level in game.get("level", []):
            name_of_levels.append(level.get("id", "Unbenanntes Level"))
    return render(request, "editor/level.html", {
        "nameOfLevels": name_of_levels
    })

def upload_json_view(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("json_file")
        if not uploaded_file:
            return render(request, "editor/start.html", {
                "error": "Keine Datei hochgeladen."
            })
        try:
            file_content = uploaded_file.read().decode("utf-8")
            game = json.loads(file_content)
        except json.JSONDecodeError:
            return render(request, "editor/start.html", {
                "error": "Die Datei ist keine gültige JSON-Datei."
            })
        name_of_levels = []
        for level in game.get("level", []):
            name_of_levels.append(level.get("id", "Unbenanntes Level"))
        return render(request, "editor/level.html", {
            "nameOfLevels": name_of_levels
        })
    return render(request, "editor/start.html")

def component_test_view(request):
    steps = [
        {"number": 1, "active": True},
        {"number": 2, "active": True},
        {"number": 3, "active": True},
        {"number": 4, "active": True},
        {"number": 5, "active": False},
        {"number": 6, "active": False},
        {"number": 7, "active": False},
        {"number": 8, "active": False},
    ]
    return render(request, "editor/test.html", {
        "steps": steps,
    })

def create_level(request):
    return render(request, "editor/createLevel.html", {
        "steps": get_steps(active_step=0),
    })

def auswahl_view(request):
    new_level = request.session.get("new_level", {})
    return render(request, "editor/auswahl.html", {
        "steps": get_steps(active_step=0),
        "new_level": new_level,
    })

def create_level1_view(request):
    steps = get_steps(active_step=1)
    saved_level = request.session.get("new_level", {})
    if request.method == "POST":
        level_id = request.POST.get("level_name", "").strip()
        start_dialog = request.POST.get("level_greeting", "").strip()
        saved_level = {}
        level_picture_name = ""
        uploaded_picture = request.FILES.get("levelPicture")
        if uploaded_picture:
            upload_dir = (Path(settings.BASE_DIR)/ "editor"/ "static"/ "editor"/ "img"/ "levels")
            upload_dir.mkdir(parents=True, exist_ok=True)
            storage = FileSystemStorage(location=upload_dir)
            level_picture_name = storage.save(uploaded_picture.name, uploaded_picture)
        saved_level["id"] = level_id
        saved_level["levelPicture"] = level_picture_name
        saved_level["startDialog"] = start_dialog
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel1 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level2")
    return render(request, "editor/createLevel1.html", {
        "steps": steps,
        "saved_level": saved_level,
    })

def create_level2_view(request):
    steps = get_steps(active_step=2)
    saved_level = request.session.get("new_level", {})
    form_values = {
        "max_columns": "",
        "max_rows": "",
        "too_many_rows_message": "",
        "too_many_columns_message": "",
        "too_many_rows_columns_message": "",}
    if request.method == "POST":
        max_columns = request.POST.get("max_columns", "").strip()
        max_rows = request.POST.get("max_rows", "").strip()
        too_many_rows_message = request.POST.get("too_many_rows_message", "").strip()
        too_many_columns_message = request.POST.get("too_many_columns_message", "").strip()
        too_many_rows_columns_message = request.POST.get("too_many_rows_columns_message", "").strip()
        saved_level["queryRestriction"] = {
            "rowRestriction": {
                "maxNumber": int(max_rows) if max_rows.isdigit() else None,
                "violationMessages": [too_many_rows_message] if too_many_rows_message else []
            },
            "columnRestriction": {
                "maxNumber": int(max_columns) if max_columns.isdigit() else None,
                "violationMessages": [too_many_columns_message] if too_many_columns_message else []
            },
            "colAndRowViolationMessages": [
                too_many_rows_columns_message
            ] if too_many_rows_columns_message else []
        }
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel2 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level3")
    return render(request, "editor/createLevel2.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
    })

def create_level3_view(request):
    steps = get_steps(active_step=3)
    saved_level = request.session.get("new_level", {})
    form_values = {
        "item_name": "",
        "unlocked_items_json": "[]",
    }
    if request.method == "POST":
        item_name = request.POST.get("item_name", "").strip()
        unlocked_items_raw = request.POST.get("unlocked_items", "[]")
        try:
            unlocked_items = json.loads(unlocked_items_raw)
        except json.JSONDecodeError:
            unlocked_items = []
        saved_level["item"] = {
            "id": item_name,
            "unlockedItems": unlocked_items
        }
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel3 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level4")
    return render(request, "editor/createLevel3.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
    })

def create_level4_view(request):
    steps = get_steps(active_step=4)
    saved_level = request.session.get("new_level", {})
    selected_item = saved_level.get("item", {})
    required_items = selected_item.get("unlockedItems", [])
    form_values = {
        "requires_password": "false",
        "required_items": required_items,
    }
    if request.method == "POST":
        requires_password = request.POST.get("requires_password") == "true"
        saved_level["unlockCondition"] = {
            "requiredItems": required_items,
            "requiresPassword": requires_password
        }
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel4 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("auswahl_view")
    return render(request, "editor/createLevel4.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
    })
