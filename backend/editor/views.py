from . import utils, sqlParser
import json, io, zipfile, sqlite3, tempfile
from pathlib import Path
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import redirect, render
from copy import deepcopy
from django.views.decorators.http import require_POST


def remember_item_summary_return(request):
    if (
            request.method == "GET"
            and request.GET.get("return_to") == "summary"
    ):
        request.session["item_creation_return_to"] = "summary"
        request.session.modified = True

    return (
        request.session.get("item_creation_return_to")
        == "summary"
    )


def set_guided_level_creation(request, active):
    if active:
        request.session["guided_level_creation"] = True
    else:
        request.session.pop("guided_level_creation", None)
    request.session.modified = True


def redirect_after_item_section_edit(
        request,
        default_view_name,
):
    if not request.session.get("item_edit_mode"):
        if request.session.get("item_creation_return_to") == "summary":
            request.session.pop("item_creation_return_to", None)
            request.session.modified = True
            return redirect("create_level7")
        return redirect(default_view_name)

    editing_item_id = request.session.get(
        "editing_item_id"
    )

    request.session.pop(
        "editing_item_section",
        None,
    )
    request.session.modified = True

    if not editing_item_id:
        return redirect(default_view_name)

    return redirect(
        "edit_item",
        item_id=editing_item_id,
    )


def redirect_after_item_password_edit(
        request,
        default_view_name,
):
    if not request.session.get("item_edit_mode"):
        if request.session.get("item_creation_return_to") == "summary":
            request.session.pop("item_creation_return_to", None)
            request.session.modified = True
            return redirect("create_level7")
        return redirect(default_view_name)
    editing_item_id = request.session.get(
        "editing_item_id"
    )
    request.session.pop(
        "editing_item_section",
        None,
    )
    request.session.modified = True
    if not editing_item_id:
        return redirect(default_view_name)
    return redirect(
        "edit_item",
        item_id=editing_item_id,
    )


def get_item_summary(saved_level):
    item = saved_level.get("item", {})
    unlock_condition = saved_level.get(
        "unlockCondition",
        {},
    )
    position = saved_level.get(
        "position",
        {},
    )

    return {
        "item_name": item.get("id", ""),
        "required_items": unlock_condition.get(
            "requiredItems",
            item.get("unlockedItems", []),
        ),
        "passwords": unlock_condition.get(
            "passwords",
            [],
        ),
        "password_hint": unlock_condition.get(
            "passwordHint",
            "",
        ),
        "success_message": unlock_condition.get(
            "successMessage",
            "",
        ),
        "failure_hints": unlock_condition.get(
            "failureHints",
            [],
        ),
        "bounding_box_image": position.get(
            "boundingBoxImage",
            {},
        ),
        "bounding_box_icon": position.get(
            "boundingBoxIcon",
            {},
        ),
        "item_type": item.get(
            "type",
            "",
        ),
        "table_name": item.get(
            "tableName",
            "",
        ),
        "columns": item.get(
            "columns",
            [],
        ),
        "text": item.get(
            "text",
            "",
        ),
        "image_link": item.get(
            "imageLink",
            "",
        ),
        "exit_success_message": item.get(
            "exitSuccessMessage",
            "",
        ),
        "next_level_id": item.get(
            "nextLevelId",
            "",
        ),
    }


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


def normalize_game_messages(game_json):
    if not isinstance(game_json, dict):
        return {}

    levels = game_json.get("level", [])
    root_messages = game_json.get("messages")

    if not isinstance(root_messages, dict):
        root_messages = None
        if isinstance(levels, list):
            for level in levels:
                if not isinstance(level, dict):
                    continue
                level_messages = level.get("messages")
                if isinstance(level_messages, dict):
                    root_messages = deepcopy(level_messages)
                    break

        if root_messages is not None:
            game_json["messages"] = root_messages
        elif "messages" in game_json:
            game_json["messages"] = {}

    if isinstance(levels, list):
        for level in levels:
            if isinstance(level, dict):
                level.pop("messages", None)

    return game_json


def get_steps(active_step):
    steps = []
    for number in range(0, 9):
        steps.append({"number": number, "active": number <= active_step})
    return steps


def start_page(request):
    set_guided_level_creation(request, False)
    return render(request, "editor/start.html")


def kontakt_view(request):
    return render(request, "editor/contact.html")


def level_view(request):
    set_guided_level_creation(request, False)
    game_json = request.session.get(
        "game_json",
        {},
    )
    levels = game_json.get(
        "level",
        [],
    )
    if not isinstance(levels, list):
        levels = []
    valid_levels = []
    for level in levels:
        if isinstance(level, dict):
            valid_levels.append(level)
    return render(
        request,
        "editor/level.html",
        {
            "levels": valid_levels,
        },
    )

def edit_level_view(
    request,
    level_id,
):
    game_json = request.session.get(
        "game_json",
        {},
    )

    if not isinstance(
        game_json,
        dict,
    ):
        return redirect(
            "level"
        )

    levels = game_json.get(
        "level",
        [],
    )

    if not isinstance(
        levels,
        list,
    ):
        return redirect(
            "level"
        )

    selected_level = next(
        (
            level
            for level in levels
            if (
                isinstance(
                    level,
                    dict,
                )
                and str(
                    level.get(
                        "id",
                        "",
                    )
                ) == str(
                    level_id
                )
            )
        ),
        None,
    )

    if selected_level is None:
        return redirect(
            "level"
        )

    clear_level_edit_session(
        request
    )

    request.session["new_level"] = (
        build_level_edit_session(
            selected_level
        )
    )

    request.session[
        "editing_level_id"
    ] = selected_level.get(
        "id",
        level_id,
    )

    request.session.modified = True

    return redirect(
        "auswahl_view"
    )

def build_clean_level_session(
    selected_level,
):
    if not isinstance(
        selected_level,
        dict,
    ):
        return {}

    items = selected_level.get(
        "items",
        [],
    )

    if not isinstance(
        items,
        list,
    ):
        items = []

    query_restriction = selected_level.get(
        "queryRestriction",
        {},
    )

    if not isinstance(
        query_restriction,
        dict,
    ):
        query_restriction = {}

    clean_level = {
        "id": selected_level.get(
            "id",
            "",
        ),
        "levelPicture": selected_level.get(
            "levelPicture",
            "",
        ),
        "databaseName": selected_level.get(
            "databaseName",
            "",
        ),
        "startDialog": selected_level.get(
            "startDialog",
            "",
        ),
        "queryRestriction": deepcopy(
            query_restriction
        ),
        "items": deepcopy(
            items
        ),
    }

    return clean_level


def clear_level_edit_session(request):
    session_keys = [
        "new_level",
        "editing_level_id",
        "editing_item_id",
        "item_edit_mode",
        "editing_item_section",
    ]

    for session_key in session_keys:
        request.session.pop(
            session_key,
            None,
        )

    request.session.modified = True

def build_level_edit_session(selected_level):
    if not isinstance(
        selected_level,
        dict,
    ):
        return {}

    query_restriction = selected_level.get(
        "queryRestriction",
        {},
    )

    if not isinstance(
        query_restriction,
        dict,
    ):
        query_restriction = {}

    items = selected_level.get(
        "items",
        [],
    )

    if not isinstance(
        items,
        list,
    ):
        items = []

    return {
        "id": selected_level.get(
            "id",
            "",
        ),
        "levelPicture": selected_level.get(
            "levelPicture",
            "",
        ),
        "databaseName": selected_level.get(
            "databaseName",
            "",
        ),
        "startDialog": selected_level.get(
            "startDialog",
            "",
        ),
        "queryRestriction": deepcopy(
            query_restriction
        ),
        "items": deepcopy(
            items
        ),
    }


def upload_json_view(request):
    if request.method != "POST":
        return render(
            request,
            "editor/start.html",
        )

    uploaded_file = request.FILES.get(
        "json_file"
    )

    if not uploaded_file:
        return render(
            request,
            "editor/start.html",
            {
                "error": "Keine Datei hochgeladen.",
            },
        )

    try:
        file_content = uploaded_file.read().decode(
            "utf-8"
        )

        game_json = json.loads(
            file_content
        )

    except UnicodeDecodeError:
        return render(
            request,
            "editor/start.html",
            {
                "error": (
                    "Die Datei konnte nicht als "
                    "UTF-8 gelesen werden."
                ),
            },
        )

    except json.JSONDecodeError:
        return render(
            request,
            "editor/start.html",
            {
                "error": (
                    "Die Datei ist keine gültige "
                    "JSON-Datei."
                ),
            },
        )

    if not isinstance(game_json, dict):
        return render(
            request,
            "editor/start.html",
            {
                "error": (
                    "Die JSON-Datei muss ein "
                    "JSON-Objekt enthalten."
                ),
            },
        )

    levels = game_json.get(
        "level",
        [],
    )

    if not isinstance(levels, list):
        return render(
            request,
            "editor/start.html",
            {
                "error": (
                    'Der Schlüssel "level" muss '
                    "eine Liste enthalten."
                ),
            },
        )

    game_json = normalize_game_messages(game_json)
    request.session["game_json"] = game_json

    request.session.pop(
        "new_level",
        None,
    )

    request.session.pop(
        "editing_level_id",
        None,
    )

    request.session.pop(
        "editing_item_id",
        None,
    )

    request.session.pop(
        "item_edit_mode",
        None,
    )

    request.session.pop(
        "editing_item_section",
        None,
    )

    request.session.modified = True
    return redirect(
        "level"
    )


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


def create_level(
    request,
):
    set_guided_level_creation(request, True)
    for session_key in [
        "editing_level_id",
        "editing_item_id",
        "item_edit_mode",
        "editing_item_section",
    ]:
        request.session.pop(
            session_key,
            None,
        )

    request.session.pop(
        "item_creation_return_to",
        None,
    )

    request.session["new_level"] = {
        "id": "",
        "levelPicture": "",
        "databaseName": "",
        "startDialog": "",
        "queryRestriction": {},
        "items": [],
    }

    request.session[
        "reset_item_draft_on_create_level3"
    ] = True

    request.session.modified = True

    return render(
        request,
        "editor/createLevel.html",
        {
            "steps": get_steps(
                active_step=0
            ),
        },
    )


def auswahl_view(request):
    set_guided_level_creation(request, False)
    new_level = request.session.get("new_level", {})
    print("Aktuelles Level:")
    print(json.dumps(new_level, ensure_ascii=False, indent=2))
    return render(
        request,
        "editor/auswahl.html",
        {
            "game_json": new_level,
        },
    )


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
            upload_dir = (Path(settings.BASE_DIR) / "editor" / "static" / "editor" / "img" / "levels")
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
            "colAndRowViolationMessages": ([too_many_rows_columns_message] if too_many_rows_columns_message else []), }
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


def create_level4_view(
    request,
):
    steps = get_steps(
        active_step=4
    )

    saved_level = request.session.get(
        "new_level",
        {},
    )

    if not isinstance(
        saved_level,
        dict,
    ):
        saved_level = {}

    if request.method == "GET":
        return_to = request.GET.get(
            "return_to",
            "",
        )
        reset_item_draft = request.session.pop(
            "reset_item_draft_on_create_level3",
            False,
        )
        if return_to == "items":
            request.session[
                "item_creation_return_to"
            ] = "items"

            saved_level.pop(
                "item",
                None,
            )

            saved_level.pop(
                "unlockCondition",
                None,
            )

            saved_level.pop(
                "position",
                None,
            )

            request.session.pop(
                "editing_item_id",
                None,
            )

            request.session.pop(
                "item_edit_mode",
                None,
            )

            request.session.pop(
                "editing_item_section",
                None,
            )

            request.session[
                "new_level"
            ] = saved_level

            request.session.modified = True

        elif return_to == "summary":
            request.session["item_creation_return_to"] = "summary"
            request.session.modified = True

        elif (
                reset_item_draft
                and not request.session.get(
                    "item_edit_mode",
                    False,
                )
        ):
            saved_level.pop(
                "item",
                None,
            )

            saved_level.pop(
                "unlockCondition",
                None,
            )

            saved_level.pop(
                "position",
                None,
            )

            request.session[
                "new_level"
            ] = saved_level

            request.session.modified = True

        elif (
                not request.session.get(
                    "item_edit_mode",
                    False,
                )
                and request.session.get(
                    "item_creation_return_to"
                ) not in {
                    "items",
                    "summary",
                    "level8",
                }
        ):
            request.session.pop(
                "item_creation_return_to",
                None,
            )

            request.session.modified = True

    return_to_item_overview = (
        request.session.get(
            "item_creation_return_to"
        )
        == "items"
    )
    return_to_item_summary = (
        request.session.get("item_creation_return_to")
        == "summary"
    )

    item = saved_level.get(
        "item",
        {},
    )

    if not isinstance(
        item,
        dict,
    ):
        item = {}

    if return_to_item_overview:
        back_url_name = "gegenstandVerwaltung"
    else:
        back_urls = {
            "table": "create_level3table",
            "hint": "create_level3hint",
            "exit": "create_level3exit",
        }
        back_url_name = back_urls.get(
            item.get("type", ""),
            "create_level3",
        )

    unlocked_items = item.get(
        "unlockedItems",
        [],
    )

    if not isinstance(
        unlocked_items,
        list,
    ):
        unlocked_items = []

    form_values = {
        "item_name": item.get(
            "id",
            "",
        ),
        "unlocked_items_json": json.dumps(
            unlocked_items,
            ensure_ascii=False,
        ),
    }

    item_options = (
        utils.get_item_options_for_current_level(
            saved_level
        )
    )
    if request.method == "POST":
        item_name = request.POST.get(
            "item_name",
            "",
        ).strip()
        unlocked_items_raw = request.POST.get(
            "unlocked_items",
            "[]",
        )
        try:
            unlocked_items = json.loads(
                unlocked_items_raw
            )
        except json.JSONDecodeError:
            unlocked_items = []
        if not isinstance(
            unlocked_items,
            list,
        ):
            unlocked_items = []
        item["id"] = item_name
        if item.get("type") == "table":
            item["tableName"] = item_name
        item["unlockedItems"] = [str(item_id).strip() for item_id in unlocked_items if str(item_id).strip()]
        saved_level["item"] = item
        request.session["new_level"] = saved_level
        request.session.modified = True
        if return_to_item_summary:
            request.session.pop("item_creation_return_to", None)
            request.session.modified = True
            return redirect("create_level7")
        if request.session.get(
            "item_edit_mode",
            False,
        ):
            editing_item_id = (
                request.session.get(
                    "editing_item_id"
                )
            )
            request.session.pop(
                "editing_item_section",
                None,
            )
            request.session.modified = True
            if editing_item_id:
                return redirect(
                    "edit_item",
                    item_id=editing_item_id,
                )
        return redirect("create_level5")
    return render(
        request,
        "editor/createLevel4.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "item_options": item_options,
            "is_item_edit": (
                request.session.get(
                    "item_edit_mode",
                    False,
                )
            ),
            "editing_item_id": (
                request.session.get(
                    "editing_item_id",
                    "",
                )
            ),
            "return_to_item_overview": (
                return_to_item_overview
            ),
            "return_to_item_summary": (
                return_to_item_summary
            ),
            "back_url_name": back_url_name,
        },
    )


def create_level3_view(request):
    steps = get_steps(active_step=3)
    saved_level = request.session.get("new_level", {})

    if request.method == "GET":
        return_to = request.GET.get("return_to", "")
        reset_item_draft = request.session.pop(
            "reset_item_draft_on_create_level3",
            False,
        )

        if return_to == "items":
            request.session["item_creation_return_to"] = "items"
            saved_level.pop("item", None)
            saved_level.pop("unlockCondition", None)
            saved_level.pop("position", None)
            request.session.pop("editing_item_id", None)
            request.session.pop("item_edit_mode", None)
            request.session.pop("editing_item_section", None)
            request.session["new_level"] = saved_level
            request.session.modified = True
        elif return_to == "summary":
            request.session["item_creation_return_to"] = "summary"
            request.session.modified = True
        elif (
            reset_item_draft
            and not request.session.get("item_edit_mode", False)
        ):
            saved_level.pop("item", None)
            saved_level.pop("unlockCondition", None)
            saved_level.pop("position", None)
            request.session["new_level"] = saved_level
            request.session.modified = True
        elif (
            not request.session.get("item_edit_mode", False)
            and request.session.get("item_creation_return_to")
            not in {"items", "summary", "level8"}
        ):
            request.session.pop("item_creation_return_to", None)
            request.session.modified = True

    return_to_item_summary = (
        request.session.get("item_creation_return_to") == "summary"
    )
    return_to_item_overview = (
        request.session.get("item_creation_return_to") == "items"
    )
    return_to_level8 = (
        request.session.get("item_creation_return_to") == "level8"
    )
    item = saved_level.get("item", {})
    form_values = {"item_type": item.get("type", "")}

    if request.method == "POST":
        return redirect("create_level31")

    return render(
        request,
        "editor/createLevel3.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_overview": return_to_item_overview,
            "return_to_item_summary": return_to_item_summary,
            "return_to_level8": return_to_level8,
        },
    )


def create_level31_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    return_to_item_overview = (
        request.session.get("item_creation_return_to") == "items"
    )
    steps = get_steps(active_step=3)
    saved_level = request.session.get("new_level", {})
    item = saved_level.get("item", {})
    type_options = [
        {"value": "table", "label": "Table"},
        {"value": "hint", "label": "Hint"},
        {"value": "exit", "label": "Exit"},
    ]
    form_values = {"item_type": item.get("type", "")}

    if request.method == "POST":
        item_type = request.POST.get("item_type", "").strip()
        if item_type not in ["table", "hint", "exit"]:
            item_type = "table"
        item["type"] = item_type
        saved_level["item"] = item
        request.session["new_level"] = saved_level
        request.session.modified = True

        if item_type == "table":
            return redirect("create_level3table")
        if item_type == "hint":
            return redirect("create_level3hint")
        return redirect("create_level3exit")

    return render(
        request,
        "editor/createLevel3-1.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "type_options": type_options,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_overview": return_to_item_overview,
            "return_to_item_summary": return_to_item_summary,
        },
    )


def create_level62_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    steps = get_steps(active_step=6)

    saved_level = request.session.get(
        "new_level",
        {},
    )

    unlock_condition = saved_level.get(
        "unlockCondition",
        {},
    )

    failure_hints = unlock_condition.get(
        "failureHints",
        [],
    )

    if not isinstance(
            failure_hints,
            list,
    ):
        failure_hints = []

    form_values = {
        "failure_hints": failure_hints,
    }

    if request.method == "POST":
        hint_attempts = request.POST.getlist(
            "hint_attempts[]"
        )

        hint_texts = request.POST.getlist(
            "hint_texts[]"
        )

        failure_hints = []

        for attempts, text in zip(
                hint_attempts,
                hint_texts,
        ):
            attempts = attempts.strip()
            text = text.strip()

            if not attempts or not text:
                continue

            if not attempts.isdigit():
                continue

            failure_hints.append(
                {
                    "attempts": int(attempts),
                    "message": text,
                }
            )

        unlock_condition = saved_level.get(
            "unlockCondition",
            {},
        )

        unlock_condition["failureHints"] = (
            failure_hints
        )

        saved_level["unlockCondition"] = (
            unlock_condition
        )

        request.session["new_level"] = (
            saved_level
        )

        request.session.modified = True

        print("createLevel6-2 gespeichert:")
        print(
            json.dumps(
                saved_level,
                ensure_ascii=False,
                indent=2,
            )
        )

        return redirect_after_item_password_edit(
            request,
            "create_level7",
        )

    return render(
        request,
        "editor/createLevel6-2.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_summary": return_to_item_summary,
        },
    )


def create_level5_view(request):
    steps = get_steps(active_step=5)
    saved_level = request.session.get("new_level", {})
    item_type = saved_level.get("item", {}).get("type", "")
    form_values = {
        "item_type": item_type,
    }
    if request.method == "POST":
        print("createLevel5 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level51")
    return render(request, "editor/createLevel5.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
        "back_url_name": "create_level4",
    })


def create_level51_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    steps = get_steps(active_step=5)
    saved_level = request.session.get("new_level", {})

    position = saved_level.get("position", {})

    bounding_box_image = position.get(
        "boundingBoxImage",
        {},
    )
    bounding_box_icon = position.get(
        "boundingBoxIcon",
        {},
    )

    level_picture = saved_level.get(
        "levelPicture",
        "",
    )

    if level_picture:
        level_picture_path = (
            f"editor/img/levels/{level_picture}"
        )

    form_values = {
        "level_picture_path": level_picture_path,
        "image_x": bounding_box_image.get(
            "x",
            "",
        ),
        "image_y": bounding_box_image.get(
            "y",
            "",
        ),
        "image_width": bounding_box_image.get(
            "width",
            "",
        ),
        "image_height": bounding_box_image.get(
            "height",
            "",
        ),
        "icon_x": bounding_box_icon.get(
            "x",
            "",
        ),
        "icon_y": bounding_box_icon.get(
            "y",
            "",
        ),
        "icon_width": bounding_box_icon.get(
            "width",
            "",
        ),
        "icon_height": bounding_box_icon.get(
            "height",
            "",
        ),
    }

    if request.method == "POST":
        saved_level["position"] = {
            "boundingBoxImage": {
                "x": int(
                    request.POST.get(
                        "image_x",
                        "0",
                    )
                ),
                "y": int(
                    request.POST.get(
                        "image_y",
                        "0",
                    )
                ),
                "width": int(
                    request.POST.get(
                        "image_width",
                        "0",
                    )
                ),
                "height": int(
                    request.POST.get(
                        "image_height",
                        "0",
                    )
                ),
            },
            "boundingBoxIcon": {
                "x": int(
                    request.POST.get(
                        "icon_x",
                        "0",
                    )
                ),
                "y": int(
                    request.POST.get(
                        "icon_y",
                        "0",
                    )
                ),
                "width": int(
                    request.POST.get(
                        "icon_width",
                        "0",
                    )
                ),
                "height": int(
                    request.POST.get(
                        "icon_height",
                        "0",
                    )
                ),
            },
        }
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel5-1 gespeichert:")
        print(
            json.dumps(
                saved_level,
                ensure_ascii=False,
                indent=2,
            )
        )
        return redirect_after_item_section_edit(
            request,
            "create_level6",
        )
    return render(
        request,
        "editor/createLevel51.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_summary": return_to_item_summary,
        },
    )


def create_level6_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    steps = get_steps(active_step=6)
    saved_level = request.session.get("new_level", {})
    unlock_condition = saved_level.get("unlockCondition", {})
    selected_item = saved_level.get("item", {})
    required_items = unlock_condition.get(
        "requiredItems",
        selected_item.get("unlockedItems", []),
    )
    requires_password = unlock_condition.get("requiresPassword", False)
    form_values = {
        "required_items": required_items,
        "requires_password": "true" if requires_password else "false",
    }
    if request.method == "POST":
        requires_password = request.POST.get("requires_password", "false") == "true"
        unlock_condition["requiredItems"] = selected_item.get("unlockedItems", [])
        unlock_condition["requiresPassword"] = requires_password

        if not requires_password:
            unlock_condition["passwords"] = []
            unlock_condition["passwordHint"] = ""
            unlock_condition["successMessage"] = ""
            unlock_condition["showHintsOnFailure"] = False
            unlock_condition["failureHints"] = []

        saved_level["unlockCondition"] = unlock_condition
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel6 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        if requires_password:
            return redirect("create_level61")
        return redirect_after_item_password_edit(request, "create_level7")
    return render(request, "editor/createLevel6.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
        "is_item_edit": request.session.get("item_edit_mode", False),
        "editing_item_id": request.session.get("editing_item_id", ""),
        "return_to_item_summary": return_to_item_summary,
    })


def create_level61_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    steps = get_steps(active_step=6)
    saved_level = request.session.get("new_level", {})
    unlock_condition = saved_level.get("unlockCondition", {})
    passwords = unlock_condition.get("passwords", [])
    if not isinstance(passwords, list):
        passwords = []
    form_values = {
        "item_passwords": ", ".join(passwords),
        "password_hint": unlock_condition.get("passwordHint", ""),
        "success_message": unlock_condition.get("successMessage", ""),
        "show_hints": "true" if unlock_condition.get("showHintsOnFailure", False) else "false",
    }
    if request.method == "POST":
        item_passwords_raw = request.POST.get("item_passwords", "").strip()
        passwords = [
            password.strip()
            for password in item_passwords_raw.replace(",", "\n").splitlines()
            if password.strip()
        ]
        show_hints = request.POST.get("show_hints", "false")
        unlock_condition["passwords"] = passwords
        unlock_condition["passwordHint"] = request.POST.get("password_hint", "").strip()
        unlock_condition["successMessage"] = request.POST.get("success_message", "").strip()
        unlock_condition["showHintsOnFailure"] = show_hints == "true"
        if show_hints != "true":
            unlock_condition["failureHints"] = []
        saved_level["unlockCondition"] = unlock_condition
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel6-1 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        if show_hints == "true":
            return redirect("create_level62")
        return redirect_after_item_password_edit(request, "create_level7")
    return render(request, "editor/createLevel6-1.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
        "is_item_edit": request.session.get("item_edit_mode", False),
        "editing_item_id": request.session.get("editing_item_id", ""),
        "return_to_item_summary": return_to_item_summary,
    })


def create_level3exit_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    return_to_item_overview = (
        request.session.get("item_creation_return_to") == "items"
    )
    steps = get_steps(active_step=3)
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
        print("createLevel3exit gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect_after_item_section_edit(
            request,
            "create_level4",
        )
    return render(request, "editor/createLevel3exit.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
        "is_item_edit": request.session.get("item_edit_mode", False),
        "editing_item_id": request.session.get("editing_item_id", ""),
        "return_to_item_overview": return_to_item_overview,
        "return_to_item_summary": return_to_item_summary,
    })


def create_level3hint_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    return_to_item_overview = (
        request.session.get("item_creation_return_to") == "items"
    )
    steps = get_steps(active_step=3)
    saved_level = request.session.get(
        "new_level",
        {},
    )
    item = saved_level.get(
        "item",
        {},
    )
    current_hint_type = item.get(
        "hintType",
        "",
    )
    hint_options = [
        {
            "value": "text",
            "label": "Über einen Text",
        },
        {
            "value": "image",
            "label": "Über ein Bild",
        },
        {
            "value": "text_image",
            "label": "Über einen Text und ein Bild",
        },
    ]
    form_values = {
        "hint_type": current_hint_type,
        "hint_text": item.get(
            "text",
            "",
        ),
        "hint_image": item.get(
            "imageLink",
            "",
        ),
    }
    if request.method == "POST":
        hint_type = request.POST.get(
            "hint_type",
            "",
        ).strip()
        hint_text = request.POST.get(
            "hint_text",
            "",
        ).strip()
        uploaded_image = request.FILES.get(
            "hint_image"
        )
        if hint_type not in [
            "text",
            "image",
            "text_image",
        ]:
            hint_type = "text"
        item = saved_level.get(
            "item",
            {},
        )
        item["type"] = "hint"
        item["hintType"] = hint_type
        if hint_type in [
            "text",
            "text_image",
        ]:
            item["text"] = hint_text
        else:
            item["text"] = ""
        if uploaded_image:
            upload_dir = (
                    Path(settings.BASE_DIR)
                    / "editor"
                    / "static"
                    / "editor"
                    / "img"
                    / "hints"
            )
            upload_dir.mkdir(
                parents=True,
                exist_ok=True,
            )
            storage = FileSystemStorage(
                location=upload_dir
            )
            filename = storage.save(
                uploaded_image.name,
                uploaded_image,
            )
            item["imageLink"] = filename
        elif hint_type == "text":
            item["imageLink"] = ""
        saved_level["item"] = item
        request.session["new_level"] = saved_level
        request.session.modified = True
        print("createLevel3hint gespeichert:")
        print(
            json.dumps(
                saved_level,
                ensure_ascii=False,
                indent=2,
            )
        )
        return redirect_after_item_section_edit(
            request,
            "create_level4",
        )
    return render(
        request,
        "editor/createLevel3hint.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "hint_options": hint_options,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_overview": return_to_item_overview,
            "return_to_item_summary": return_to_item_summary,
        },
    )


def create_level3table_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    return_to_item_overview = (
        request.session.get("item_creation_return_to") == "items"
    )
    steps = get_steps(active_step=3)

    saved_level = request.session.get(
        "new_level",
        {},
    )

    item = saved_level.get(
        "item",
        {},
    )

    data_type_options = [
        {
            "value": "text",
            "label": "Text",
        },
        {
            "value": "number",
            "label": "Zahl",
        },
        {
            "value": "date",
            "label": "Datum",
        },
        {
            "value": "boolean",
            "label": "Boolean",
        },
    ]

    form_values = {
        "table_name": item.get(
            "tableName",
            item.get("id", ""),
        ),
        "columns": item.get(
            "columns",
            [],
        ),
        "rows": item.get(
            "rows",
            [],
        ),
    }

    error_message = ""

    if request.method == "POST":
        column_ids = request.POST.getlist(
            "column_ids[]"
        )

        column_types = request.POST.getlist(
            "column_types[]"
        )

        columns = []

        for column_id, column_type in zip(
                column_ids,
                column_types,
        ):
            column_id = column_id.strip()
            column_type = column_type.strip()

            if not column_id and not column_type:
                continue

            if not column_id:
                error_message = (
                    "Jede Spalte benötigt einen Namen."
                )
                break

            if column_type not in {
                "text",
                "number",
                "date",
                "boolean",
            }:
                error_message = (
                    f"Der Datentyp der Spalte "
                    f"„{column_id}“ ist ungültig."
                )
                break

            if any(
                    existing_column["id"].lower()
                    == column_id.lower()
                    for existing_column in columns
            ):
                error_message = (
                    f"Der Spaltenname "
                    f"„{column_id}“ wurde mehrfach verwendet."
                )
                break

            columns.append(
                {
                    "id": column_id,
                    "type": column_type,
                }
            )

        rows = []

        raw_rows_json = request.POST.get(
            "rows_json",
            "[]",
        )

        if not error_message:
            try:
                submitted_rows = json.loads(
                    raw_rows_json
                )
            except json.JSONDecodeError:
                submitted_rows = []
                error_message = (
                    "Die Tabellendaten konnten nicht "
                    "verarbeitet werden."
                )

        if not error_message:
            if not isinstance(
                    submitted_rows,
                    list,
            ):
                submitted_rows = []

            for submitted_row in submitted_rows:
                if not isinstance(
                        submitted_row,
                        dict,
                ):
                    continue

                cleaned_row = {}
                row_has_value = False

                for column in columns:
                    column_id = column["id"]
                    column_type = column["type"]

                    raw_value = submitted_row.get(
                        column_id,
                        "",
                    )

                    cleaned_value = (
                        utils.convert_table_cell_value(
                            raw_value,
                            column_type,
                        )
                    )

                    if cleaned_value not in (
                            "",
                            None,
                    ):
                        row_has_value = True

                    cleaned_row[column_id] = (
                        cleaned_value
                    )

                if row_has_value:
                    rows.append(cleaned_row)

        form_values = {
            "table_name": item.get(
                "id",
                "",
            ),
            "columns": columns,
            "rows": rows,
        }

        if not columns and not error_message:
            error_message = (
                "Lege mindestens eine Tabellenspalte an."
            )

        if not error_message:
            item_name = item.get(
                "id",
                "",
            )

            item["type"] = "table"
            item["tableName"] = item_name
            item["columns"] = columns
            item["rows"] = rows

            saved_level["item"] = item

            request.session["new_level"] = (
                saved_level
            )

            request.session.modified = True

            print(
                "createLevel3table gespeichert:"
            )

            print(
                json.dumps(
                    saved_level,
                    ensure_ascii=False,
                    indent=2,
                )
            )

            return redirect_after_item_section_edit(
                request,
                "create_level4",
            )

    return render(
        request,
        "editor/createLevel3table.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "data_type_options": (
                data_type_options
            ),
            "error_message": error_message,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_overview": return_to_item_overview,
            "return_to_item_summary": return_to_item_summary,
        },
    )


def create_level7_view(request):
    steps = get_steps(active_step=7)
    saved_level = request.session.get(
        "new_level",
        {},
    )
    requires_password = saved_level.get(
        "unlockCondition",
        {},
    ).get("requiresPassword", False)
    summary = get_item_summary(saved_level)
    if request.method == "POST":
        print("createLevel7 Übersicht:")
        print(
            json.dumps(
                saved_level,
                ensure_ascii=False,
                indent=2,
            )
        )
        return redirect("create_level8")
    return render(
        request,
        "editor/createLevel7.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "summary": summary,
            "back_url_name": (
                "create_level62"
                if requires_password
                else "create_level6"
            ),
        },
    )


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

        game_json, saved_level = utils.save_new_level_to_game_json(
            request
        )
        if next_action == "more_items":
            saved_level.pop("item", None)
            saved_level.pop("unlockCondition", None)
            saved_level.pop("position", None)
            request.session["item_creation_return_to"] = "level8"
            request.session["new_level"] = saved_level
            request.session["game_json"] = game_json
            request.session.modified = True

            print(
                "Gegenstand wurde in die JSON eingefügt. "
                "Neuer Gegenstand kann erstellt werden:"
            )
            print(json.dumps(game_json, ensure_ascii=False, indent=2, ))
            return redirect("create_level3")
        if next_action == "item_management":
            request.session["new_level"] = saved_level
            request.session["game_json"] = game_json
            request.session.modified = True
            print(
                "Gegenstand wurde in die JSON eingefügt. "
                "Weiter zur Gegenstandsverwaltung:"
            )
            print(
                json.dumps(
                    game_json,
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return redirect("gegenstandVerwaltung")
        request.session["new_level"] = saved_level
        request.session["game_json"] = game_json
        request.session.modified = True
        print(
            "Gegenstand wurde in die JSON eingefügt. "
            "Zurück zur Auswahl:"
        )
        print(
            json.dumps(
                game_json,
                ensure_ascii=False,
                indent=2,
            )
        )
        return redirect("auswahl_view")
    return render(
        request,
        "editor/createLevel8.html",
        {
            "steps": steps,
            "saved_level": saved_level,
        },
    )


def export_game_view(request):
    game_json = request.session.get(
        "game_json",
        {},
    )
    if not isinstance(
        game_json,
        dict,
    ):
        game_json = {}

    (
        export_game_json,
        asset_files,
    ) = utils.prepare_game_json_for_export(
        game_json,
        settings.BASE_DIR,
    )

    zip_buffer = io.BytesIO()

    with tempfile.TemporaryDirectory() as temp_directory:
        temp_directory = Path(
            temp_directory
        )
        with zipfile.ZipFile(
            zip_buffer,
            "w",
            zipfile.ZIP_DEFLATED,
        ) as zip_file:
            levels = export_game_json.get(
                "level",
                [],
            )
            if not isinstance(
                levels,
                list,
            ):
                levels = []

            for level_index, level in enumerate(
                levels
            ):
                if not isinstance(
                    level,
                    dict,
                ):
                    continue
                level_id = level.get(
                    "id",
                    f"level{level_index}",
                )
                level_folder = level.pop(
                    "_exportFolder",
                    utils.sanitize_export_name(
                        level_id,
                        fallback=(
                            f"level{level_index}"
                        ),
                    ),
                )
                safe_level_id = (
                    utils.sanitize_export_name(
                        level_id,
                        fallback=(
                            f"level{level_index}"
                        ),
                    )
                )
                level_sql = (
                    sqlParser.build_level_sql(
                        level
                    )
                )
                sql_archive_path = (
                    f"{level_folder}/databases/"
                    f"create_{safe_level_id}.sql"
                )
                database_archive_path = (
                    f"{level_folder}/databases/"
                    f"{safe_level_id}.db"
                )
                zip_file.writestr(
                    sql_archive_path,
                    level_sql,
                )
                database_path = (
                    temp_directory
                    / (
                        f"{safe_level_id}_"
                        f"{level_index}.db"
                    )
                )
                connection = sqlite3.connect(
                    database_path
                )
                try:
                    if level_sql.strip():
                        connection.executescript(
                            level_sql
                        )

                    connection.commit()

                finally:
                    connection.close()

                zip_file.write(
                    database_path,
                    database_archive_path,
                )
            json_string = json.dumps(
                export_game_json,
                ensure_ascii=False,
                indent=2,
            )
            zip_file.writestr(
                "SQLSpellQuest.json",
                json_string,
            )
            for (
                archive_path,
                source_path,
            ) in asset_files.items():
                zip_file.write(
                    source_path,
                    archive_path,
                )
    zip_buffer.seek(0)
    response = HttpResponse(
        zip_buffer.getvalue(),
        content_type="application/zip",
    )
    response[
        "Content-Disposition"
    ] = (
        'attachment; '
        'filename="SQLSpellQuest_export.zip"'
    )
    return response

def level_grunddaten_view(request):
    set_guided_level_creation(request, False)
    saved_level = request.session.get("new_level", {})

    if request.method == "POST":
        level_name = request.POST.get(
            "level_name",
            "",
        ).strip()

        level_greeting = request.POST.get(
            "level_greeting",
            "",
        ).strip()

        uploaded_picture = request.FILES.get(
            "levelPicture"
        )

        if uploaded_picture:
            upload_dir = (
                    Path(settings.BASE_DIR)
                    / "editor"
                    / "static"
                    / "editor"
                    / "img"
                    / "levels"
            )

            upload_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            storage = FileSystemStorage(
                location=upload_dir
            )

            level_picture_name = storage.save(
                uploaded_picture.name,
                uploaded_picture,
            )

            saved_level["levelPicture"] = (
                level_picture_name
            )

        saved_level["id"] = level_name
        saved_level["startDialog"] = level_greeting

        request.session["new_level"] = saved_level
        request.session.modified = True
        print("Level-Grunddaten:")
        print(
            json.dumps(
                saved_level,
                ensure_ascii=False,
                indent=2
            )
        )
        return redirect("auswahl_view")

    form_values = {
        "level_name": saved_level.get("id", ""),
        "level_picture": saved_level.get(
            "levelPicture",
            "",
        ),
        "level_greeting": saved_level.get(
            "startDialog",
            "",
        ),
    }
    return render(
        request,
        "editor/levelGrunddaten.html",
        {
            "form_values": form_values,
        },
    )


def sql_grunddaten_view(request):
    set_guided_level_creation(request, False)
    saved_level = request.session.get("new_level", {})

    query_restriction = saved_level.get(
        "queryRestriction",
        {}
    )

    row_restriction = query_restriction.get(
        "rowRestriction",
        {}
    )

    column_restriction = query_restriction.get(
        "columnRestriction",
        {}
    )

    row_messages = row_restriction.get(
        "violationMessages",
        []
    )

    column_messages = column_restriction.get(
        "violationMessages",
        []
    )

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
            "colAndRowViolationMessages": (
                [too_many_rows_columns_message]
                if too_many_rows_columns_message
                else []
            ),
        }

        request.session["new_level"] = saved_level
        request.session.modified = True

        print("SQL-Grunddaten gespeichert:")
        print(
            json.dumps(
                saved_level,
                ensure_ascii=False,
                indent=2
            )
        )

        return redirect("auswahl_view")

    return render(
        request,
        "editor/sqlGrunddaten.html",
        {
            "saved_level": saved_level,
            "form_values": form_values,
        },
    )


def gegenstand_view(
    request,
):
    set_guided_level_creation(request, False)
    saved_level = request.session.get(
        "new_level",
        {},
    )

    if not isinstance(
        saved_level,
        dict,
    ):
        saved_level = {}

    items = saved_level.get(
        "items",
        [],
    )

    if not isinstance(
        items,
        list,
    ):
        items = []

    clean_saved_level = {
        **saved_level,
        "items": deepcopy(
            items
        ),
    }

    return render(
        request,
        "editor/gegenstandVerwaltung.html",
        {
            "saved_level": clean_saved_level,
            "steps": get_steps(
                active_step=1
            ),
        },
    )


def edit_item_view(request, item_id):
    set_guided_level_creation(request, False)
    saved_level = request.session.get(
        "new_level",
        {},
    )

    currently_edited_item = (
        request.session.get(
            "editing_item_id"
        )
    )

    if currently_edited_item != item_id:
        selected_item = (
            utils.load_item_for_editing(
                saved_level,
                item_id,
            )
        )

        if selected_item is None:
            print(
                f"Gegenstand '{item_id}' "
                "wurde nicht gefunden."
            )

            return redirect(
                "gegenstandVerwaltung"
            )

        request.session["new_level"] = (
            saved_level
        )
        request.session[
            "editing_item_id"
        ] = item_id

        request.session.modified = True

    summary = get_item_summary(
        saved_level
    )

    if request.method == "POST":
        old_item_id = (
            request.session.get(
                "editing_item_id",
                item_id,
            )
        )

        current_item = (
            utils.build_item_for_json(
                saved_level
            )
        )

        items = saved_level.get(
            "items",
            [],
        )

        updated_items = []
        item_replaced = False

        for existing_item in items:
            if (
                    existing_item.get("id")
                    == old_item_id
            ):
                updated_items.append(
                    current_item
                )
                item_replaced = True
            else:
                updated_items.append(
                    existing_item
                )

        if not item_replaced:
            updated_items.append(
                current_item
            )

        saved_level["items"] = (
            updated_items
        )

        request.session["new_level"] = (
            saved_level
        )
        request.session.modified = True

        game_json, saved_level = (
            utils.save_new_level_to_game_json(
                request
            )
        )

        request.session["new_level"] = (
            saved_level
        )
        request.session["game_json"] = (
            game_json
        )

        request.session.pop(
            "item_edit_mode",
            None,
        )
        request.session.pop(
            "editing_item_id",
            None,
        )
        request.session.pop(
            "editing_item_section",
            None,
        )

        request.session.modified = True

        print(
            "Bearbeiteter Gegenstand "
            "gespeichert:"
        )
        print(
            json.dumps(
                current_item,
                ensure_ascii=False,
                indent=2,
            )
        )

        return redirect(
            "gegenstandVerwaltung"
        )

    return render(
        request,
        "editor/editItem.html",
        {
            "saved_level": saved_level,
            "summary": summary,
            "item_id": item_id,
        },
    )


def edit_item_section_view(
        request,
        item_id,
        section,
):
    set_guided_level_creation(request, False)
    allowed_sections = {
        "grunddaten": "create_level4",
        "passwort": "create_level6",
        "position": "create_level51",
        "typ": "create_level31",
        "table": "create_level3table",
        "hint": "create_level3hint",
        "exit": "create_level3exit",
    }
    target_view = allowed_sections.get(
        section
    )
    if target_view is None:
        return redirect(
            "edit_item",
            item_id=item_id,
        )
    request.session.pop(
        "item_creation_return_to",
        None,
    )
    request.session[
        "item_edit_mode"
    ] = True
    request.session[
        "editing_item_id"
    ] = item_id
    request.session[
        "editing_item_section"
    ] = section
    request.session.modified = True
    return redirect(
        target_view
    )


def cancel_item_edit_view(request):
    request.session.pop(
        "item_edit_mode",
        None,
    )
    request.session.pop(
        "editing_item_id",
        None,
    )
    request.session.pop(
        "editing_item_section",
        None,
    )
    request.session.modified = True
    return redirect(
        "gegenstandVerwaltung"
    )


DEFAULT_MESSAGES = {
    "wrong_password": (
        "Das Passwort ist nicht korrekt. "
        "Versuche es bitte erneut."
    ),
    "wrong_password_new_hint": (
        "Das Passwort ist nicht korrekt. "
        "Ein neuer Hinweis wurde freigeschaltet."
    ),
    "not_a_table": (
        "Auf %s kann keine SQL-Abfrage ausgeführt werden, "
        "da es sich nicht um eine Tabelle handelt."
    ),
    "unknown_table": (
        "Die Tabelle ist nicht bekannt. "
        "Checke bitte den Tabellennamen."
    ),
    "locked_table": (
        "Die Tabelle ist noch nicht freigeschaltet."
    ),
    "sql_error": (
        "Die SQL-Abfrage konnte nicht gecallt werden. "
        "Check bitte die Syntax und versuche es erneut."
    ),
    "no_result": (
        "Die SQL-Abfrage hat kein Ergebnis geliefert."
    ),
    "row_restriction": (
        "Die Abfrage liefert zu viele Zeilen. "
        "Limitiere das Ergebnis bitte auf die notwendigen Zeilen ein."
    ),
    "col_restriction": (
        "Die Abfrage liefert zu viele Spalten. "
        "Choose bitte nur die benötigten Spalten aus."
    ),
    "row_and_col_restriction": (
        "Die Abfrage liefert zu viele Zeilen und Spalten. "
        "Limitiere das Ergebnis bitte auf die benötigten Zeilen "
        "und Spalten ein."
    ),
}


def messages_grunddaten_view(request):
    set_guided_level_creation(request, False)
    game_json = request.session.get(
        "game_json",
        {},
    )
    game_json = normalize_game_messages(game_json)

    saved_messages = game_json.get(
        "messages",
        {},
    )

    form_values = {
        key: saved_messages.get(
            key,
            default_value,
        )
        for key, default_value
        in DEFAULT_MESSAGES.items()
    }
    if request.method == "POST":
        messages = {}
        for key, default_value in DEFAULT_MESSAGES.items():
            value = request.POST.get(
                key,
                "",
            ).strip()
            messages[key] = (
                value
                if value
                else default_value
            )
        game_json["messages"] = messages
        request.session["game_json"] = game_json
        request.session.modified = True
        print("Systemnachrichten gespeichert:")
        print(
            json.dumps(
                game_json,
                ensure_ascii=False,
                indent=2,
            )
        )
        return redirect(
            "auswahl_view"
        )

    return render(
        request,
        "editor/messagesGrunddaten.html",
        {
            "form_values": form_values,
        },
    )


def delete_item_view(request, item_id):
    if request.method != "POST":
        return redirect(
            "gegenstandVerwaltung"
        )

    saved_level = request.session.get(
        "new_level",
        {},
    )

    level_id = saved_level.get(
        "id",
        "",
    )

    saved_level = utils.remove_item_from_level(
        saved_level,
        item_id,
    )

    save_new_level_session(
        request,
        saved_level,
    )
    game_json = request.session.get(
        "game_json",
        {},
    )

    levels = game_json.get(
        "level",
        [],
    )

    if isinstance(levels, list) and level_id:
        updated_levels = []

        for level in levels:
            if (
                    isinstance(level, dict)
                    and level.get("id") == level_id
            ):
                level = utils.remove_item_from_level(
                    level,
                    item_id,
                )

            updated_levels.append(level)

        game_json["level"] = updated_levels
        request.session["game_json"] = game_json

    if request.session.get("editing_item_id") == item_id:
        request.session.pop(
            "item_edit_mode",
            None,
        )

        request.session.pop(
            "editing_item_id",
            None,
        )

        request.session.pop(
            "editing_item_section",
            None,
        )

    request.session.modified = True
    print("Systemnachrichten gespeichert:")
    print(
        json.dumps(
            game_json,
            ensure_ascii=False,
            indent=2,
        )
    )

    return redirect(
        "gegenstandVerwaltung"
    )


@require_POST
def save_level_view(request):
    saved_level = request.session.get(
        "new_level",
        {},
    )

    if not isinstance(saved_level, dict):
        return redirect("auswahl_view")

    saved_level.pop("messages", None)
    saved_level = utils.save_current_item_to_new_level(
        saved_level
    )
    level_for_json = utils.build_level_for_json(
        saved_level
    )

    level_id = str(
        level_for_json.get("id", "")
    ).strip()

    if not level_id:
        return redirect("levelGrunddaten")

    game_json = request.session.get(
        "game_json",
        {},
    )

    if not isinstance(game_json, dict):
        game_json = {}

    game_json = normalize_game_messages(game_json)

    levels = game_json.get(
        "level",
        [],
    )

    if not isinstance(levels, list):
        levels = []

    editing_level_id = request.session.get(
        "editing_level_id"
    )

    updated_levels = []
    level_was_replaced = False

    for level in levels:
        if not isinstance(level, dict):
            updated_levels.append(level)
            continue

        existing_level_id = level.get("id")

        should_replace = (
                editing_level_id
                and existing_level_id == editing_level_id
        )

        if not editing_level_id:
            should_replace = (
                    existing_level_id == level_id
            )

        if should_replace and not level_was_replaced:
            updated_levels.append(
                deepcopy(level_for_json)
            )
            level_was_replaced = True
        else:
            updated_levels.append(level)

    if not level_was_replaced:
        updated_levels.append(
            deepcopy(level_for_json)
        )

    game_json["level"] = updated_levels

    request.session["game_json"] = game_json

    request.session.pop(
        "editing_level_id",
        None,
    )
    request.session.pop(
        "editing_item_id",
        None,
    )
    request.session.pop(
        "item_edit_mode",
        None,
    )
    request.session.pop(
        "editing_item_section",
        None,
    )
    request.session.pop(
        "new_level",
        None,
    )
    request.session.modified = True
    print("Systemnachrichten gespeichert:")
    print(
        json.dumps(
            game_json,
            ensure_ascii=False,
            indent=2,
        )
    )
    return redirect("level")


@require_POST
def delete_level_view(request, level_id):
    game_json = request.session.get("game_json", {})

    levels = game_json.get("level", [])

    if isinstance(levels, list):
        game_json["level"] = [

            level

            for level in levels

            if not (

                    isinstance(level, dict)

                    and level.get("id") == level_id

            )

        ]

    request.session["game_json"] = game_json

    if request.session.get("editing_level_id") == level_id:
        request.session.pop("editing_level_id", None)

        request.session.pop("new_level", None)

    request.session.modified = True
    print("Systemnachrichten gespeichert:")
    print(
        json.dumps(
            game_json,
            ensure_ascii=False,
            indent=2,
        )
    )
    return redirect("level")
