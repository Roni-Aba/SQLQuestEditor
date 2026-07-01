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

        if requires_password:
            return redirect("create_level41")

        return redirect("create_level5")
    return render(request, "editor/createLevel4.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
    })

def create_level41_view(request):
    steps = get_steps(active_step=5)
    saved_level = request.session.get("new_level", {})
    form_values = {
        "item_passwords": "",
        "password_hint": "",
        "success_message": "",
        "show_hints": "false",
    }
    if request.method == "POST":
        item_passwords_raw = request.POST.get("item_passwords", "").strip()
        password_hint = request.POST.get("password_hint", "").strip()
        success_message = request.POST.get("success_message", "").strip()
        show_hints = request.POST.get("show_hints", "false")
        passwords = [
            p.strip()
            for p in item_passwords_raw.replace(",", "\n").splitlines()
            if p.strip()
        ]
        unlock_condition = saved_level.get("unlockCondition", {})
        unlock_condition["passwords"] = passwords
        unlock_condition["passwordHint"] = password_hint
        unlock_condition["successMessage"] = success_message
        unlock_condition["showHintsOnFailure"] = show_hints == "true"
        saved_level["unlockCondition"] = unlock_condition
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel5 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        if show_hints == "true":
            return redirect("create_level42")
        return redirect("create_level5")
    return render(request, "editor/createLevel4-1.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
    })

def create_level42_view(request):
    steps = get_steps(active_step=5)
    saved_level = request.session.get("new_level", {})
    if request.method == "POST":
        hint_attempts = request.POST.getlist("hint_attempts[]")
        hint_texts = request.POST.getlist("hint_texts[]")
        failure_hints = []
        for attempts, text in zip(hint_attempts, hint_texts):
            attempts = attempts.strip()
            text = text.strip()
            if not attempts or not text:
                continue
            if not attempts.isdigit():
                continue
            failure_hints.append({
                "attempts": int(attempts),
                "message": text,
            })
        unlock_condition = saved_level.get("unlockCondition", {})
        unlock_condition["failureHints"] = failure_hints
        saved_level["unlockCondition"] = unlock_condition
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel4-2 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level5")
    return render(request, "editor/createLevel4-2.html", {
        "steps": steps,
        "saved_level": saved_level,
    })

def create_level5_view(request):
    steps = get_steps(active_step=5)
    saved_level = request.session.get("new_level", {})
    unlock_condition = saved_level.get("unlockCondition", {})
    required_items = unlock_condition.get("requiredItems", [])
    requires_password = unlock_condition.get("requiresPassword", False)
    form_values = {
        "required_items": required_items,
        "requires_password": requires_password,
    }
    if request.method == "POST":
        print("createLevel5 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level51")

    return render(request, "editor/createLevel5.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
    })

def create_level51_view(request):
    steps = get_steps(active_step=5)
    saved_level = request.session.get("new_level", {})

    position = saved_level.get("position", {})

    bounding_box_image = position.get("boundingBoxImage", {})
    bounding_box_icon = position.get("boundingBoxIcon", {})

    level_picture = saved_level.get("levelPicture", "")

    if level_picture:
        level_picture_path = f"editor/img/levels/{level_picture}"
    else:
        level_picture_path = "editor/img/magie1.png"

    form_values = {
        "level_picture_path": level_picture_path,

        "image_x": bounding_box_image.get("x", ""),
        "image_y": bounding_box_image.get("y", ""),
        "image_width": bounding_box_image.get("width", ""),
        "image_height": bounding_box_image.get("height", ""),

        "icon_x": bounding_box_icon.get("x", ""),
        "icon_y": bounding_box_icon.get("y", ""),
        "icon_width": bounding_box_icon.get("width", ""),
        "icon_height": bounding_box_icon.get("height", ""),
    }

    if request.method == "POST":
        saved_level["position"] = {
            "boundingBoxImage": {
                "x": int(request.POST.get("image_x", "")),
                "y": int(request.POST.get("image_y", "")),
                "width": int(request.POST.get("image_width", "")),
                "height": int(request.POST.get("image_height", "")),
            },
            "boundingBoxIcon": {
                "x": int(request.POST.get("icon_x", "")),
                "y": int(request.POST.get("icon_y", "")),
                "width": int(request.POST.get("icon_width", "")),
                "height": int(request.POST.get("icon_height", "")),
            },
        }
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel5-1 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level6")
    return render(request, "editor/createLevel51.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
    })

def create_level6_view(request):
    steps = get_steps(active_step=6)
    saved_level = request.session.get("new_level", {})
    unlock_condition = saved_level.get("unlockCondition", {})
    required_items = unlock_condition.get("requiredItems", [])
    requires_password = unlock_condition.get("requiresPassword", False)
    form_values = {
        "required_items": required_items,
        "requires_password": requires_password,
    }
    if request.method == "POST":
        print("createLevel6 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level61")
    return render(request, "editor/createLevel6.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
    })
def create_level61_view(request):
    steps = get_steps(active_step=6)
    saved_level = request.session.get("new_level", {})
    item = saved_level.get("item", {})
    current_type = item.get("type", "")
    type_options = [
        {"value": "table", "label": "Table"},
        {"value": "hint", "label": "Hint"},
        {"value": "exit", "label": "Exit"},
]
    form_values = {"item_type": current_type,}
    if request.method == "POST":
        item_type = request.POST.get("item_type", "").strip()
        if item_type not in ["table", "hint", "exit"]:
            item_type = "table"
        item = saved_level.get("item", {})
        item["type"] = item_type
        saved_level["item"] = item
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel6-1 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        if item_type == "table":
            return redirect("create_level6table")
        if item_type == "hint":
            return redirect("create_level6hint")
        if item_type == "exit":
            return redirect("create_level6exit")
    return render(request, "editor/createLevel61.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
        "type_options": type_options,
    })
def create_level6exit_view(request):
    steps = get_steps(active_step=6)
    saved_level = request.session.get("new_level", {})
    item = saved_level.get("item", {})
    form_values = {
        "exit_success_message": item.get("exitSuccessMessage", ""),
        "next_level_id": item.get("nextLevelId", ""),
    }
    if request.method == "POST":
        exit_success_message = request.POST.get("exit_success_message", "").strip()
        next_level_id = request.POST.get("next_level_id", "").strip()
        item = saved_level.get("item", {})
        item["type"] = "exit"
        item["exitSuccessMessage"] = exit_success_message
        item["nextLevelId"] = next_level_id
        saved_level["item"] = item
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel6exit gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level7")
    return render(request, "editor/createLevel6exit.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
    })

def create_level6hint_view(request):
    steps = get_steps(active_step=6)
    saved_level = request.session.get("new_level", {})
    item = saved_level.get("item", {})
    current_hint_type = item.get("hintType", "")
    hint_options = [
        {"value": "text", "label": "Über einen Text"},
        {"value": "image", "label": "Über ein Bild"},
        {"value": "text_image", "label": "Über ein Text und ein Bild"},
    ]
    form_values = {
        "hint_type": current_hint_type,
        "hint_text": item.get("text", ""),
        "hint_image": item.get("imageLink", ""),
    }
    if request.method == "POST":
        hint_type = request.POST.get("hint_type", "").strip()
        hint_text = request.POST.get("hint_text", "").strip()
        uploaded_image = request.FILES.get("hint_image")
        if hint_type not in ["text", "image", "text_image"]:
            hint_type = "text"
        item = saved_level.get("item", {})
        item["type"] = "hint"
        item["hintType"] = hint_type
        if hint_type in ["text", "text_image"]:
            item["text"] = hint_text
        else:
            item["text"] = ""
        if uploaded_image:
            upload_dir = settings.BASE_DIR / "editor" / "static" / "editor" / "img" / "hints"
            upload_dir.mkdir(parents=True, exist_ok=True)
            storage = FileSystemStorage(location=upload_dir)
            filename = storage.save(uploaded_image.name, uploaded_image)
            item["imageLink"] = filename
        elif hint_type == "text":
            item["imageLink"] = item.get("imageLink", "")
        else:
            item["imageLink"] = item.get("imageLink", "")
        saved_level["item"] = item
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel6hint gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level7")
    return render(request, "editor/createLevel6hint.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
        "hint_options": hint_options,
    })


def create_level6table_view(request):
    steps = get_steps(active_step=6)
    saved_level = request.session.get("new_level", {})
    item = saved_level.get("item", {})
    data_type_options = [
        {"value": "text", "label": "Text"},
        {"value": "number", "label": "Zahl"},
        {"value": "date", "label": "Datum"},
        {"value": "boolean", "label": "Boolean"},
    ]
    form_values = {
        "table_name": item.get("tableName", ""),
        "columns": item.get("columns", []),
    }
    if request.method == "POST":
        column_ids = request.POST.getlist("column_ids[]")
        column_types = request.POST.getlist("column_types[]")
        columns = []
        for column_id, column_type in zip(column_ids, column_types):
            column_id = column_id.strip()
            column_type = column_type.strip()
            if not column_id and not column_type:
                continue
            columns.append({
                "id": column_id,
                "type": column_type,
            })
        item_name = item.get("id", "")
        item = saved_level.get("item", {})
        item["type"] = "table"
        item["tableName"] = item_name + ".sql"
        item["columns"] = columns
        saved_level["item"] = item
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel6table gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level7")
    return render(request, "editor/createLevel6table.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
        "data_type_options": data_type_options,
    })

def create_level7_view(request):
    return render(request,"editor/createLevel7.html", {})