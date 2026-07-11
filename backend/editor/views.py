from . import utils, sqlParser
import json, io, zipfile
from pathlib import Path
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import redirect, render

def first_or_empty(values):
    return values[0] if values else ""

def parse_optional_int(value):
    value = str(value).strip()
    if value.isdigit():
        return int(value)
    return None

def save_new_level_session(request, saved_level):
    request.session["new_level"] = saved_level
    request.session.modified = True

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
        request.session["game_json"] = game
        request.session.modified = True
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
    game_json = request.session.get("game_json", {})
    print("Aktuelle gesamte JSON in auswahl_view:")
    print(json.dumps(game_json, ensure_ascii=False, indent=2))
    return render(request, "editor/auswahl.html", {
        "game_json": game_json,
    })

def create_level1_view(request):
    steps = get_steps(active_step=1)
    saved_level = request.session.get("new_level", {})
    form_values = {
        "level_name": saved_level.get("id", ""),
        "level_greeting": saved_level.get("startDialog", ""),
        "level_picture": saved_level.get("levelPicture", ""),
    }
    if request.method == "POST":
        level_id = request.POST.get("level_name", "").strip()
        start_dialog = request.POST.get("level_greeting", "").strip()
        saved_level["id"] = level_id
        saved_level["startDialog"] = start_dialog
        uploaded_picture = request.FILES.get("levelPicture")
        if uploaded_picture:
            upload_dir = (Path(settings.BASE_DIR)/ "editor"/ "static"/ "editor"/ "img"/ "levels")
            upload_dir.mkdir(parents=True, exist_ok=True)
            storage = FileSystemStorage(location=upload_dir)
            level_picture_name = storage.save(
                uploaded_picture.name,
                uploaded_picture
            )
            saved_level["levelPicture"] = level_picture_name
        save_new_level_session(request, saved_level)
        print("createLevel1 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level2")
    return render(request, "editor/createLevel1.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
    })

def create_level2_view(request):
    steps = get_steps(active_step=2)
    saved_level = request.session.get("new_level", {})
    query_restriction = saved_level.get("queryRestriction", {})
    row_restriction = query_restriction.get("rowRestriction", {})
    column_restriction = query_restriction.get("columnRestriction", {})
    row_messages = row_restriction.get("violationMessages", [])
    column_messages = column_restriction.get("violationMessages", [])
    row_column_messages = query_restriction.get(
        "colAndRowViolationMessages",
        []
    )
    form_values = {
        "max_columns": (
            column_restriction.get("maxNumber")
            if column_restriction.get("maxNumber") is not None
            else ""
        ),
        "max_rows": (
            row_restriction.get("maxNumber")
            if row_restriction.get("maxNumber") is not None
            else ""
        ),
        "too_many_rows_message": (
            row_messages[0]
            if row_messages
            else ""
        ),
        "too_many_columns_message": (
            column_messages[0]
            if column_messages
            else ""
        ),
        "too_many_rows_columns_message": (
            row_column_messages[0]
            if row_column_messages
            else ""
        ),
    }
    if request.method == "POST":
        max_columns = request.POST.get(
            "max_columns",
            ""
        ).strip()

        max_rows = request.POST.get(
            "max_rows",
            ""
        ).strip()

        too_many_rows_message = request.POST.get(
            "too_many_rows_message",
            ""
        ).strip()

        too_many_columns_message = request.POST.get(
            "too_many_columns_message",
            ""
        ).strip()

        too_many_rows_columns_message = request.POST.get(
            "too_many_rows_columns_message",
            ""
        ).strip()
        saved_level["queryRestriction"] = {
            "rowRestriction": {
                "maxNumber": (
                    int(max_rows)
                    if max_rows.isdigit()
                    else None
                ),
                "violationMessages": (
                    [too_many_rows_message]
                    if too_many_rows_message
                    else []
                ),
            },
            "columnRestriction": {
                "maxNumber": (
                    int(max_columns)
                    if max_columns.isdigit()
                    else None
                ),
                "violationMessages": (
                    [too_many_columns_message]
                    if too_many_columns_message
                    else []
                ),
            },
            "colAndRowViolationMessages": ([too_many_rows_columns_message] if too_many_rows_columns_message else []),}
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel2 gespeichert:")
        print(json.dumps(saved_level,ensure_ascii=False,indent=2))
        return redirect("create_level3")
    return render(request, "editor/createLevel2.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
    })

def create_level3_view(request):
    steps = get_steps(active_step=3)
    saved_level = request.session.get("new_level", {})
    current_item = saved_level.get("item", {})
    item_options = utils.get_item_options_for_current_level(saved_level)
    unlocked_items = current_item.get("unlockedItems",[])
    if not isinstance(unlocked_items, list):
        unlocked_items = []
    form_values = {
        "item_name": current_item.get("id", ""),
        "unlocked_items_json": json.dumps(
            unlocked_items,
            ensure_ascii=False
        ),
    }
    if request.method == "POST":
        item_name = request.POST.get(
            "item_name",
            ""
        ).strip()
        unlocked_items_raw = request.POST.get(
            "unlocked_items",
            "[]"
        )
        try:
            unlocked_items = json.loads(unlocked_items_raw)
            if not isinstance(unlocked_items, list):
                unlocked_items = []
        except (json.JSONDecodeError, TypeError):
            unlocked_items = []
        current_item = saved_level.get("item", {})
        current_item["id"] = item_name
        current_item["unlockedItems"] = unlocked_items
        saved_level["item"] = current_item
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel3 gespeichert:")
        print(json.dumps(saved_level,ensure_ascii=False,indent=2))
        return redirect("create_level4")
    return render(request, "editor/createLevel3.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
        "item_options": item_options,
    })
def create_level4_view(request):
    steps = get_steps(active_step=4)
    saved_level = request.session.get("new_level", {})
    selected_item = saved_level.get("item", {})
    unlock_condition = saved_level.get("unlockCondition", {})
    required_items = unlock_condition.get("requiredItems",selected_item.get("unlockedItems", []))
    requires_password = unlock_condition.get("requiresPassword",False)
    form_values = {
        "requires_password": (
            "true" if requires_password else "false"),
        "required_items": required_items,
    }
    if request.method == "POST":
        requires_password = (request.POST.get("requires_password","false")== "true")
        selected_item = saved_level.get("item", {})
        required_items = selected_item.get("unlockedItems",[])
        unlock_condition = saved_level.get("unlockCondition",{})
        unlock_condition["requiredItems"] = required_items
        unlock_condition["requiresPassword"] = requires_password
        saved_level["unlockCondition"] = unlock_condition
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel4 gespeichert:")
        print(json.dumps(saved_level,ensure_ascii=False,indent=2))
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
    unlock_condition = saved_level.get("unlockCondition", {})
    passwords = unlock_condition.get("passwords", [])
    if not isinstance(passwords, list):
        passwords = []
    form_values = {
        "item_passwords": ", ".join(passwords),
        "password_hint": unlock_condition.get(
            "passwordHint",
            ""
        ),
        "success_message": unlock_condition.get(
            "successMessage",
            ""
        ),
        "show_hints": (
            "true"
            if unlock_condition.get(
                "showHintsOnFailure",
                False
            )
            else "false"
        ),
    }
    if request.method == "POST":
        item_passwords_raw = request.POST.get("item_passwords","").strip()
        password_hint = request.POST.get("password_hint","").strip()
        success_message = request.POST.get("success_message","").strip()
        show_hints = request.POST.get("show_hints","false")
        passwords = [
            password.strip()
            for password in item_passwords_raw
            .replace(",", "\n")
            .splitlines()
            if password.strip()
]
        unlock_condition = saved_level.get("unlockCondition",{})
        unlock_condition["passwords"] = passwords
        unlock_condition["passwordHint"] = password_hint
        unlock_condition["successMessage"] = success_message
        unlock_condition["showHintsOnFailure"] = (show_hints == "true")
        saved_level["unlockCondition"] = unlock_condition
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel4-1 gespeichert:")
        print(json.dumps(saved_level,ensure_ascii=False,indent=2))
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
    unlock_condition = saved_level.get("unlockCondition",{})
    failure_hints = unlock_condition.get("failureHints",[])
    if not isinstance(failure_hints, list):
        failure_hints = []
    form_values = {"failure_hints": failure_hints,}
    if request.method == "POST":
        hint_attempts = request.POST.getlist("hint_attempts[]")
        hint_texts = request.POST.getlist("hint_texts[]")
        failure_hints = []
        for attempts, text in zip(hint_attempts,hint_texts):
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
        unlock_condition = saved_level.get("unlockCondition",{})
        unlock_condition["failureHints"] = failure_hints
        saved_level["unlockCondition"] = unlock_condition
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel4-2 gespeichert:")
        print(json.dumps(saved_level,ensure_ascii=False,indent=2))
        return redirect("create_level5")
    return render(request, "editor/createLevel4-2.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
    })

def create_level5_view(request):
    steps = get_steps(active_step=5)
    saved_level = request.session.get("new_level", {})
    unlock_condition = saved_level.get("unlockCondition",{})
    required_items = unlock_condition.get("requiredItems",[])
    requires_password = unlock_condition.get("requiresPassword",False)
    show_hints_on_failure = unlock_condition.get("showHintsOnFailure",False)
    if show_hints_on_failure:
        back_url_name = "create_level42"
    elif requires_password:
        back_url_name = "create_level41"
    else:
        back_url_name = "create_level4"
    form_values = {
        "required_items": required_items,
        "requires_password": requires_password,
        "show_hints_on_failure": show_hints_on_failure,
    }
    if request.method == "POST":
        print("createLevel5 gespeichert:")
        print(json.dumps(saved_level,ensure_ascii=False,indent=2))
        return redirect("create_level51")
    return render(request, "editor/createLevel5.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
        "back_url_name": back_url_name,
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
        item["tableName"] = item_name
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
    steps = get_steps(active_step=7)
    saved_level = request.session.get("new_level", {})

    item = saved_level.get("item", {})
    unlock_condition = saved_level.get("unlockCondition", {})
    position = saved_level.get("position", {})

    summary = {
        "item_name": item.get("id", ""),
        "required_items": unlock_condition.get("requiredItems", item.get("unlockedItems", [])),
        "passwords": unlock_condition.get("passwords", []),
        "password_hint": unlock_condition.get("passwordHint", ""),
        "success_message": unlock_condition.get("successMessage", ""),
        "failure_hints": unlock_condition.get("failureHints", []),
        "bounding_box_image": position.get("boundingBoxImage", {}),
        "bounding_box_icon": position.get("boundingBoxIcon", {}),
        "item_type": item.get("type", ""),
        "table_name": item.get("tableName", ""),
        "columns": item.get("columns", []),
        "text": item.get("text", ""),
        "image_link": item.get("imageLink", ""),
        "exit_success_message": item.get("exitSuccessMessage", ""),
        "next_level_id": item.get("nextLevelId", ""),
    }
    if request.method == "POST":
        print("createLevel7 Übersicht:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level8")

    return render(request, "editor/createLevel7.html", {
        "steps": steps,
        "saved_level": saved_level,
        "summary": summary,
    })

def save_current_item_to_level(saved_level):
    item = saved_level.get("item", {})

    if not item.get("id"):
        return saved_level

    items = saved_level.get("items", [])

    existing_index = None
    for index, existing_item in enumerate(items):
        if existing_item.get("id") == item.get("id"):
            existing_index = index
            break

    if existing_index is not None:
        items[existing_index] = item
    else:
        items.append(item)

    saved_level["items"] = items
    return saved_level


def create_level8_view(request):
    steps = get_steps(active_step=8)
    saved_level = request.session.get("new_level", {})
    if request.method == "POST":
        next_action = request.POST.get("next_action")
        game_json, saved_level = utils.save_new_level_to_game_json(request)
        if next_action == "more_items":
            saved_level.pop("item", None)
            saved_level.pop("unlockCondition", None)
            saved_level.pop("position", None)
            request.session["new_level"] = saved_level
            request.session["game_json"] = game_json
            request.session.modified = True
            print("Gegenstand wurde in die JSON eingefügt. Neuer Gegenstand kann erstellt werden:")
            print(json.dumps(game_json, ensure_ascii=False, indent=2))
            return redirect("create_level3")
        request.session["new_level"] = saved_level
        request.session["game_json"] = game_json
        request.session.modified = True
        print("Gegenstand wurde in die JSON eingefügt. Zurück zur Auswahl:")
        print(json.dumps(game_json, ensure_ascii=False, indent=2))

        return redirect("auswahl_view")

    return render(request, "editor/createLevel8.html", {
        "steps": steps,
        "saved_level": saved_level,
    })

def export_game_view(request):
    game_json = request.session.get("game_json", {})
    json_string = json.dumps(game_json, ensure_ascii=False, indent=2)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(
            "SQLSpellQuest_export.json",
            json_string
        )
        for level in game_json.get("level", []):
            level_id = level.get("id", "level")
            level_sql = sqlParser.build_level_sql(level)
            if not level_sql.strip():
                continue
            sql_filename = f"{level_id}.sql"
            zip_file.writestr(
                sql_filename,
                level_sql
            )
    zip_buffer.seek(0)
    response = HttpResponse(
        zip_buffer.getvalue(),
        content_type="application/zip"
    )
    response["Content-Disposition"] = 'attachment; filename="SQLSpellQuest_export.zip"'
    return response

