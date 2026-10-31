from . import database, utils
from copy import deepcopy
import json, io, zipfile, sqlite3, tempfile, shutil
from pathlib import Path, PurePosixPath
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from .services.level_basics import (
    level1_form_values,
    level2_form_values,
    query_restriction_from_post,
)
from .services.item_draft import (
    clear_item_draft,
    item_type_and_next_view,
    clear_table_data_on_type_change,
    parse_unlocked_item,
    has_item_name_conflict,
    set_item_requirements,
    set_item_name_and_sync_table,
    remove_item_from_game_levels,
    remove_deleted_table_rows
)
from .services.item_edit import (
    find_item,
    load_item_draft,
    preserve_original_item_fields,
    sync_edited_table_rows,
    replace_item_and_update_references,
)

from .services.level_save import (
    replace_or_append_level,
    update_exit_level_references,
    update_import_sources,
)
from .services.level_delete import (
    referencing_level_ids,
    remove_level_from_list,
)
from .services.game_import import (
    select_game_json_entry,
    copy_uploaded_files,
    build_import_sources,
    build_import_manifest,
)
from .services.game_export import (
    write_level_databases,
    write_prepared_assets,
    write_imported_files,
)

from .services.table_editor import (
    parse_table_columns,
    parse_table_rows,
    persist_draft_table_rows
)

from .services.item_position import (
    _box_from_post,
    position_from_post,
    position_form_values
)

from .services.hint_editor import update_hint_field, update_hint_image
from .services.exit_editor import update_exit_fields
from .services.item_summary import get_item_summary
from .services.item_unlock import (
    update_password_requirement,
    update_password_details,
    failure_hints_from_post,

)

from .services.game_messages import (
    DEFAULT_MESSAGES,
    normalize_game_messages,
    messages_form_values,
    messages_from_post,
)

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


def first_or_empty(values):
    return values[0] if values else ""


def parse_optional_int(value):
    value = str(value).strip()
    if value.isdigit():
        return int(value)
    return None


def level_name_is_taken(game_json, level_name, editing_level_id=None):
    levels = game_json.get("level", []) if isinstance(game_json, dict) else []
    if not isinstance(levels, list):
        return False
    return any(
        isinstance(level, dict)
        and level.get("id") == level_name
        and level.get("id") != editing_level_id
        for level in levels
    )


def current_level_origin_id(request, saved_level):
    origin_id = (
        request.session.get("editing_level_id")
        or request.session.get("auto_saved_level_id")
    )
    if origin_id:
        return origin_id

    game_json = request.session.get("game_json", {})
    levels = game_json.get("level", []) if isinstance(game_json, dict) else []
    if not isinstance(levels, list):
        return None

    draft = utils.build_level_for_json(saved_level)
    if draft.get("id") and draft in levels:
        return draft["id"]
    return None


def save_new_level_session(request, saved_level):
    request.session["new_level"] = saved_level
    request.session.modified = True


def clear_editor_state(request):
    for session_key in [
        "new_level",
        "auto_saved_level_id",
        "editing_level_id",
        "editing_item_id",
        "item_edit_mode",
        "editing_item_section",
        "item_creation_return_to",
    ]:
        request.session.pop(session_key, None)



def get_steps(active_step):
    steps = []
    for number in range(0, 9):
        steps.append({"number": number, "active": number <= active_step})
    return steps


def start_page(request):
    set_guided_level_creation(request, False)
    return render(request, "editor/start.html")


def new_game_view(request):
    if request.method != "POST":
        return redirect("start")

    request.session["game_json"] = {
        "id": "SQLSpellQuest",
        "messages": deepcopy(DEFAULT_MESSAGES),
        "level": [],
    }
    request.session.pop("game_workspace", None)
    request.session.pop("game_root", None)
    request.session.pop("import_sources", None)
    request.session.pop("import_json_path", None)
    request.session.pop("import_manifest", None)
    database.start_new_editor_workspace(request)
    clear_editor_state(request)
    request.session.modified = True

    return redirect("level")


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
            "error_message": request.session.pop("level_error", ""),
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

    level_draft = build_level_edit_session(selected_level)
    source = request.session.get("import_sources", {}).get(str(level_id), {})
    level_draft["_import_table_sources"] = deepcopy(source.get("tables", {}))
    database.begin_editor_level_rows(request, level_draft)
    request.session["new_level"] = level_draft

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
    database.discard_editor_level_rows(request, request.session.get("new_level"))
    session_keys = [
        "new_level",
        "auto_saved_level_id",
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

    uploaded_files = request.FILES.getlist("game_files")
    legacy_json_file = request.FILES.get("json_file")

    if not uploaded_files and legacy_json_file:
        uploaded_files = [legacy_json_file]

    if not uploaded_files:
        return render(
            request,
            "editor/start.html",
            {
                "error": "Kein Spielordner ausgewählt.",
            },
        )

    relative_names = request.POST.getlist("game_relative_paths")
    if len(relative_names) != len(uploaded_files):
        relative_names = [
            str(game_file.name)
            for game_file in uploaded_files
        ]

    uploaded_entries = list(zip(uploaded_files, relative_names))
    uploaded_entry = select_game_json_entry(uploaded_entries)

    if uploaded_entry is None:
        return render(
            request,
            "editor/start.html",
            {
                "error": (
                    "Im Spielordner wurde keine eindeutige JSON-Datei "
                    "gefunden. Benenne sie bitte SQLSpellQuest.json "
                    "oder Game.json."
                ),
            },
        )

    uploaded_file, json_relative_name = uploaded_entry

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

    workspace_path = Path(
        tempfile.mkdtemp(prefix="sql-quest-game-")
    )
    json_relative_path = PurePosixPath(
        str(json_relative_name).replace("\\", "/")
    )

    try:
        copy_uploaded_files(workspace_path, uploaded_entries)
    except (OSError, ValueError) as error:
        shutil.rmtree(workspace_path, ignore_errors=True)
        return render(
            request,
            "editor/start.html",
            {
                "error": str(error),
            },
        )

    if not isinstance(game_json, dict):
        shutil.rmtree(workspace_path, ignore_errors=True)
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
        shutil.rmtree(workspace_path, ignore_errors=True)
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

    previous_workspace = request.session.get("game_workspace")
    previous_game_root = request.session.get("game_root")
    request.session["game_workspace"] = str(workspace_path)
    game_root = workspace_path.joinpath(
        *json_relative_path.parent.parts
    )
    request.session["game_root"] = str(game_root)
    try:
        game_json = database.initialize_editor_table_rows(
            request,
            normalize_game_messages(game_json),
        )
    except sqlite3.Error as error:
        shutil.rmtree(workspace_path, ignore_errors=True)
        if previous_workspace is None:
            request.session.pop("game_workspace", None)
        else:
            request.session["game_workspace"] = previous_workspace
        if previous_game_root is None:
            request.session.pop("game_root", None)
        else:
            request.session["game_root"] = previous_game_root
        request.session.modified = True
        return render(
            request,
            "editor/start.html",
            {
                "error": (
                    "Die Level-Datenbank konnte nicht gelesen werden: "
                    f"{error}"
                ),
            },
        )
    import_sources = build_import_sources(request, game_json, game_root)
    request.session["import_sources"] = import_sources
    request.session["import_json_path"] = str(game_root / json_relative_path.name)
    request.session["import_manifest"] = build_import_manifest(
        game_root, import_sources
    )
    clear_editor_state(request)
    request.session["game_json"] = game_json

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
    database.discard_editor_level_rows(request, request.session.get("new_level"))
    for session_key in [
        "auto_saved_level_id",
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
    form_values = level1_form_values(saved_level)

    if request.method == "POST":
        level_id = request.POST.get("level_name", "").strip()
        start_dialog = request.POST.get("level_greeting", "").strip()
        if level_name_is_taken(request.session.get("game_json", {}), level_id):
            return render(request, "editor/createLevel1.html", {
                "steps": steps,
                "saved_level": saved_level,
                "form_values": {
                    "level_name": level_id,
                    "level_greeting": start_dialog,
                    "level_picture": saved_level.get("levelPicture", ""),
                },
                "error_message": f'Der Levelname "{level_id}" wird bereits verwendet.',
            })

        saved_level["id"] = level_id
        saved_level["databaseName"] = utils.database_name_for_level(level_id)
        database.finalize_editor_level_rows(
            request,
            saved_level,
            level_id,
        )
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
            saved_level.setdefault("_new_asset_sources", {})[
                level_picture_name
            ] = str(upload_dir / level_picture_name)
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
    form_values = level2_form_values(saved_level)

    if request.method == "POST":
        saved_level["queryRestriction"] = query_restriction_from_post(request.POST)
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


def create_level4_view(request):
    steps = get_steps(active_step=4)
    saved_level = request.session.get("new_level", {})

    if not isinstance(saved_level, dict):
        saved_level = {}

    if request.method == "GET":
        return_to = request.GET.get("return_to", "")
        reset_item_draft = request.session.pop(
            "reset_item_draft_on_create_level3",
            False,
        )

        if return_to == "items":
            request.session["item_creation_return_to"] = "items"
            clear_item_draft(saved_level)

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
            clear_item_draft(saved_level)

            request.session["new_level"] = saved_level
            request.session.modified = True

        elif (
            not request.session.get("item_edit_mode", False)
            and request.session.get("item_creation_return_to")
            not in {"items", "summary", "level8"}
        ):
            request.session.pop("item_creation_return_to", None)
            request.session.modified = True

    return_to_item_overview = (
        request.session.get("item_creation_return_to") == "items"
    )
    return_to_item_summary = (
        request.session.get("item_creation_return_to") == "summary"
    )

    item = saved_level.get("item", {})
    if not isinstance(item, dict):
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

    unlocked_items = item.get("unlockedItems", [])
    if not isinstance(unlocked_items, list):
        unlocked_items = []

    form_values = {
        "item_name": item.get("id", ""),
        "unlocked_items_json": json.dumps(
            unlocked_items,
            ensure_ascii=False,
        ),
    }

    item_options = utils.get_item_options_for_current_level(saved_level)
    error_message = ""
    if request.method == "POST":
        item_name = request.POST.get("item_name", "").strip()
        unlocked_items = parse_unlocked_item(
            request.POST.get("unlocked_items", "[]")
        )
        editing_item_id = request.session.get("editing_item_id", "")
        name_conflict = has_item_name_conflict(saved_level, item, item_name, editing_item_id)
        if name_conflict:
            error_message = (
                f'Der Gegenstands- oder Tabellenname "{item_name}" '
                "wird in diesem Level bereits verwendet."
            )
            form_values["item_name"] = item_name
        else:
            set_item_name_and_sync_table(request, saved_level, item, item_name)
            set_item_requirements(saved_level, item, unlocked_items)

            saved_level["item"] = item
            request.session["new_level"] = saved_level
            request.session.modified = True

            if return_to_item_summary:
                request.session.pop("item_creation_return_to", None)
                request.session.modified = True
                return redirect("create_level7")

            if request.session.get("item_edit_mode", False):
                request.session.pop("editing_item_section", None)
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
            "error_message": error_message,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_overview": return_to_item_overview,
            "return_to_item_summary": return_to_item_summary,
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
            clear_item_draft(saved_level)
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
            clear_item_draft(saved_level)
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
        item_type, next_view = item_type_and_next_view(request.POST)
        clear_table_data_on_type_change(
            request,
            saved_level,
            item,
            item_type,
        )

        item["type"] = item_type
        saved_level["item"] = item
        request.session["new_level"] = saved_level
        request.session.modified = True

        return redirect(next_view)

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
    saved_level = request.session.get("new_level", {})
    unlock_condition = saved_level.get("unlockCondition", {})

    failure_hints = unlock_condition.get("failureHints", [])
    if not isinstance(failure_hints, list):
        failure_hints = []

    form_values = {
        "failure_hints": failure_hints,
    }

    if request.method == "POST":
        unlock_condition["failureHints"] = failure_hints_from_post(
            request.POST
        )

        saved_level["unlockCondition"] = unlock_condition
        request.session["new_level"] = saved_level
        request.session.modified = True

        print("createLevel6-2 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))

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
    form_values = position_form_values(saved_level)

    if request.method == "POST":
        saved_level["position"] = position_from_post(request.POST)
        request.session["new_level"] = saved_level
        request.session.modified = True

        print("createLevel5-1 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))

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
        requires_password = update_password_requirement(
            unlock_condition,
            selected_item,
            request.POST,
        )

        saved_level["unlockCondition"] = unlock_condition
        request.session["new_level"] = saved_level
        request.session.modified = True

        print("createLevel6 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))

        if requires_password:
            return redirect("create_level61")

        return redirect_after_item_password_edit(
            request,
            "create_level7",
        )

    return render(
        request,
        "editor/createLevel6.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_summary": return_to_item_summary,
        },
    )


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
        "show_hints": (
            "true"
            if unlock_condition.get("showHintsOnFailure", False)
            else "false"
        ),
    }

    if request.method == "POST":
        show_hints = update_password_details(
            unlock_condition,
            request.POST,
        )

        saved_level["unlockCondition"] = unlock_condition
        request.session["new_level"] = saved_level
        request.session.modified = True

        print("createLevel6-1 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))

        if show_hints:
            return redirect("create_level62")

        return redirect_after_item_password_edit(
            request,
            "create_level7",
        )

    return render(
        request,
        "editor/createLevel6-1.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_summary": return_to_item_summary,
        },
    )


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
        update_exit_fields(item, request.POST)

        saved_level["item"] = item
        request.session["new_level"] = saved_level
        request.session.modified = True

        print("createLevel3exit gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))

        return redirect_after_item_section_edit(
            request,
            "create_level4",
        )
    return render(
        request,
        "editor/createLevel3exit.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_overview": return_to_item_overview,
            "return_to_item_summary": return_to_item_summary,
        },
    )


def create_level3hint_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    return_to_item_overview = (
        request.session.get("item_creation_return_to") == "items"
    )
    steps = get_steps(active_step=3)
    saved_level = request.session.get("new_level", {})
    item = saved_level.get("item", {})

    current_hint_type = item.get("hintType", "")
    hint_options = [
        {"value": "text", "label": "Über einen Text"},
        {"value": "image", "label": "Über ein Bild"},
        {"value": "text_image", "label": "Über einen Text und ein Bild"},
    ]
    form_values = {
        "hint_type": current_hint_type,
        "hint_text": item.get("text", ""),
        "hint_image": item.get("imageLink", ""),
    }

    if request.method == "POST":
        hint_type = update_hint_field(item, request.POST)
        uploaded_image = request.FILES.get("hint_image")

        update_hint_image(item, saved_level, uploaded_image, hint_type, settings.BASE_DIR,)

        saved_level["item"] = item
        request.session["new_level"] = saved_level
        request.session.modified = True

        print("createLevel3hint gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))

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
    saved_level = request.session.get("new_level", {})
    item = saved_level.get("item", {})

    data_type_options = [
        {"value": "text", "label": "Text"},
        {"value": "number", "label": "Zahl"},
        {"value": "date", "label": "Datum"},
        {"value": "boolean", "label": "Boolean"},
    ]

    form_values = {
        "table_name": item.get("tableName", item.get("id", "")),
        "columns": item.get("columns", []),
        "rows": item.get("rows", []),
    }
    error_message = ""

    if request.method == "POST":
        columns, error_message = parse_table_columns(
            request.POST.getlist("column_ids[]"),
            request.POST.getlist("column_types[]"),
        )

        rows = []
        raw_rows_json = request.POST.get("rows_json", "[]")

        if not error_message:
            rows, error_message = parse_table_rows(
                raw_rows_json,
                columns,
            )

        form_values = {
            "table_name": item.get("id", ""),
            "columns": columns,
            "rows": rows,
        }

        if not columns and not error_message:
            error_message = "Lege mindestens eine Tabellenspalte an."

        if not error_message and not request.session.get("item_edit_mode"):
            persist_draft_table_rows(request, saved_level, item, rows)

        if not error_message:
            item_name = str(item.get("id", "")).strip()

            item["type"] = "table"
            item["tableName"] = item_name
            item["columns"] = columns
            item["rows"] = rows

            saved_level["item"] = item
            request.session["new_level"] = saved_level
            request.session.modified = True

            print("createLevel3table gespeichert:")
            print(json.dumps(saved_level, ensure_ascii=False, indent=2))

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
            "data_type_options": data_type_options,
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
    unlock_condition = saved_level.get("unlockCondition", {})
    if not unlock_condition.get("requiresPassword", False):
        back_url_name = "create_level6"
    elif unlock_condition.get("showHintsOnFailure", False):
        back_url_name = "create_level62"
    else:
        back_url_name = "create_level61"
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
            "back_url_name": back_url_name,
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
        game_json, saved_level = utils.save_new_level_to_game_json(request)

        if next_action == "more_items":
            clear_item_draft(saved_level)
            request.session["item_creation_return_to"] = "level8"

        request.session["new_level"] = saved_level
        request.session["game_json"] = game_json
        request.session.modified = True

        if next_action == "more_items":
            print(
                "Gegenstand wurde in die JSON eingefügt. "
                "Neuer Gegenstand kann erstellt werden:"
            )
            print(json.dumps(game_json, ensure_ascii=False, indent=2))
            return redirect("create_level3")

        if next_action == "item_management":
            print(
                "Gegenstand wurde in die JSON eingefügt. "
                "Weiter zur Gegenstandsverwaltung:"
            )
            print(json.dumps(game_json, ensure_ascii=False, indent=2))
            return redirect("gegenstandVerwaltung")

        print(
            "Gegenstand wurde in die JSON eingefügt. "
            "Zurück zur Auswahl:"
        )
        print(json.dumps(game_json, ensure_ascii=False, indent=2))
        return redirect("auswahl_view")

    return render(
        request,
        "editor/createLevel8.html",
        {
            "steps": steps,
            "saved_level": saved_level,
        },
    )


def _build_game_export(request):
    game_json = request.session.get("game_json", {})
    if not isinstance(game_json, dict):
        game_json = {}

    export_game_json, asset_files = utils.prepare_game_json_for_export(
        game_json,
        settings.BASE_DIR,
        request.session.get("game_root"),
        request.session.get("import_sources", {}),
    )

    zip_buffer = io.BytesIO()
    managed_archive_paths = {"SQLSpellQuest.json"}

    with tempfile.TemporaryDirectory() as temp_directory:
        with zipfile.ZipFile(
            zip_buffer, "w", zipfile.ZIP_DEFLATED
        ) as zip_file:
            write_level_databases(
                request,
                zip_file,
                export_game_json,
                Path(temp_directory),
                managed_archive_paths,
            )
            json_string = json.dumps(
                export_game_json, ensure_ascii=False, indent=2
            )
            zip_file.writestr("SQLSpellQuest.json", json_string)
            write_prepared_assets(zip_file, asset_files)
            write_imported_files(
                request, zip_file, asset_files, managed_archive_paths
            )

    zip_buffer.seek(0)
    response = HttpResponse(
        zip_buffer.getvalue(),
        content_type="application/zip",
    )
    response["Content-Disposition"] = (
        'attachment; filename="SQLSpellQuest_export.zip"'
    )
    return response


def export_game_view(request):
    try:
        return _build_game_export(request)
    except (OSError, sqlite3.Error, ValueError) as error:
        game_json = request.session.get("game_json", {})
        levels = game_json.get("level", []) if isinstance(game_json, dict) else []
        return render(request, "editor/level.html", {
            "levels": levels if isinstance(levels, list) else [],
            "error_message": f"Export fehlgeschlagen: {error}",
        }, status=400)

def level_grunddaten_view(request):
    set_guided_level_creation(request, False)
    saved_level = request.session.get("new_level", {})
    form_values = level1_form_values(saved_level)

    if request.method == "POST":
        level_name = request.POST.get("level_name", "").strip()
        level_greeting = request.POST.get("level_greeting", "").strip()

        if level_name_is_taken(
            request.session.get("game_json", {}),
            level_name,
            current_level_origin_id(request, saved_level),
        ):
            form_values["level_name"] = level_name
            form_values["level_greeting"] = level_greeting
            return render(
                request,
                "editor/levelGrunddaten.html",
                {
                    "form_values": form_values,
                    "error_message": (
                        f'Der Levelname "{level_name}" wird bereits verwendet.'
                    ),
                },
            )

        uploaded_picture = request.FILES.get("levelPicture")
        if uploaded_picture:
            upload_dir = (
                Path(settings.BASE_DIR)
                / "editor"
                / "static"
                / "editor"
                / "img"
                / "levels"
            )
            upload_dir.mkdir(parents=True, exist_ok=True)

            storage = FileSystemStorage(location=upload_dir)
            level_picture_name = storage.save(
                uploaded_picture.name,
                uploaded_picture,
            )
            saved_level["levelPicture"] = level_picture_name
            saved_level.setdefault("_new_asset_sources", {})[
                level_picture_name
            ] = str(upload_dir / level_picture_name)

        saved_level["id"] = level_name
        saved_level["databaseName"] = utils.database_name_for_level(level_name)

        if not request.session.get("editing_level_id"):
            database.finalize_editor_level_rows(
                request,
                saved_level,
                level_name,
            )

        saved_level["startDialog"] = level_greeting
        request.session["new_level"] = saved_level
        request.session.modified = True

        print("Level-Grunddaten:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("auswahl_view")

    return render(
        request,
        "editor/levelGrunddaten.html",
        {"form_values": form_values},
    )


def sql_grunddaten_view(request):
    set_guided_level_creation(request, False)
    saved_level = request.session.get("new_level", {})
    form_values = level2_form_values(saved_level)

    if request.method == "POST":
        saved_level["queryRestriction"] = query_restriction_from_post(
            request.POST
        )
        request.session["new_level"] = saved_level
        request.session.modified = True

        print("SQL-Grunddaten gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
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
    saved_level = request.session.get("new_level", {})

    currently_edited_item = request.session.get("editing_item_id")
    if currently_edited_item != item_id:
        selected_item = load_item_draft(request, saved_level, item_id)
        if selected_item is None:
            print(f"Gegenstand '{item_id}' wurde nicht gefunden.")
            return redirect("gegenstandVerwaltung")

        request.session["new_level"] = saved_level
        request.session["editing_item_id"] = item_id
        request.session.modified = True

    summary = get_item_summary(saved_level)

    if request.method == "POST":
        old_item_id = request.session.get("editing_item_id", item_id)
        current_item = utils.build_item_for_json(saved_level)
        items = saved_level.get("items", [])
        original_item = find_item(items, old_item_id)

        preserve_original_item_fields(
            current_item, original_item, saved_level
        )
        sync_edited_table_rows(
            request, saved_level, current_item, original_item
        )
        saved_level["items"] = replace_item_and_update_references(
            items, old_item_id, current_item
        )

        request.session["new_level"] = saved_level
        request.session.modified = True

        if request.session.get("editing_level_id"):
            game_json = request.session.get("game_json", {})
        else:
            game_json, saved_level = utils.save_new_level_to_game_json(request)

        clear_item_draft(saved_level)
        request.session["new_level"] = saved_level
        request.session["game_json"] = game_json

        request.session.pop("item_edit_mode", None)
        request.session.pop("editing_item_id", None)
        request.session.pop("editing_item_section", None)
        request.session.pop("item_creation_return_to", None)
        request.session.modified = True

        print("Bearbeiteter Gegenstand gespeichert:")
        print(json.dumps(current_item, ensure_ascii=False, indent=2))
        return redirect("gegenstandVerwaltung")

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
    saved_level = request.session.get("new_level")
    if isinstance(saved_level, dict):
        for draft_key in ("item", "unlockCondition", "position"):
            saved_level.pop(draft_key, None)
        request.session["new_level"] = saved_level

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



def messages_grunddaten_view(request):
    set_guided_level_creation(request, False)
    game_json = request.session.get("game_json", {})
    game_json = normalize_game_messages(game_json)

    saved_messages = game_json.get("messages", {})
    form_values = messages_form_values(saved_messages)

    if request.method == "POST":
        game_json["messages"] = messages_from_post(request.POST)
        request.session["game_json"] = game_json
        request.session.modified = True

        print("Systemnachrichten gespeichert:")
        print(json.dumps(game_json, ensure_ascii=False, indent=2))
        return redirect("auswahl_view")

    return render(
        request,
        "editor/messagesGrunddaten.html",
        {"form_values": form_values},
    )


def delete_item_view(request, item_id):
    if request.method != "POST":
        return redirect("gegenstandVerwaltung")

    saved_level = request.session.get("new_level", {})
    level_id = saved_level.get("id", "")

    remove_deleted_table_rows(request, saved_level, item_id)

    saved_level = utils.remove_item_from_level(saved_level, item_id)
    save_new_level_session(request, saved_level)

    game_json = request.session.get("game_json", {})
    levels = game_json.get("level", [])

    if isinstance(levels, list) and level_id:
        game_json["level"] = remove_item_from_game_levels(
            levels,
            level_id,
            item_id,
        )
        request.session["game_json"] = game_json

    if request.session.get("editing_item_id") == item_id:
        request.session.pop("item_edit_mode", None)
        request.session.pop("editing_item_id", None)
        request.session.pop("editing_item_section", None)

    request.session.modified = True
    print("Systemnachrichten gespeichert:")
    print(json.dumps(game_json, ensure_ascii=False, indent=2))
    return redirect("gegenstandVerwaltung")


@require_POST
def save_level_view(request):
    saved_level = request.session.get("new_level", {})

    if not isinstance(saved_level, dict):
        return redirect("auswahl_view")

    saved_level.pop("messages", None)
    if request.session.get("editing_item_id"):
        for draft_key in ("item", "unlockCondition", "position"):
            saved_level.pop(draft_key, None)
    else:
        saved_level = utils.save_current_item_to_new_level(saved_level)

    level_for_json = utils.build_level_for_json(saved_level)
    level_id = str(level_for_json.get("id", "")).strip()

    if not level_id:
        return redirect("levelGrunddaten")

    editing_level_id = current_level_origin_id(request, saved_level)
    game_json = request.session.get("game_json", {})
    if level_name_is_taken(game_json, level_id, editing_level_id):
        return redirect("levelGrunddaten")

    has_table_draft = bool(saved_level.get(database.EDITOR_LEVEL_DRAFT_KEY))
    database.finalize_editor_level_rows(request, saved_level, level_id)

    if not isinstance(game_json, dict):
        game_json = {}
    game_json = normalize_game_messages(game_json)

    levels = game_json.get("level", [])
    if not isinstance(levels, list):
        levels = []

    updated_levels = replace_or_append_level(
        levels,
        level_for_json,
        editing_level_id,
    )
    update_exit_level_references(
        updated_levels,
        editing_level_id,
        level_id,
    )

    game_json["level"] = updated_levels
    request.session["game_json"] = game_json

    import_sources = request.session.get("import_sources", {})
    if update_import_sources(
        import_sources,
        saved_level,
        editing_level_id,
        level_id,
    ):
        request.session["import_sources"] = import_sources

    if editing_level_id and editing_level_id != level_id:
        if has_table_draft:
            database.remove_editor_level_rows(request, editing_level_id)
        else:
            database.move_editor_level_rows(
                request,
                editing_level_id,
                level_id,
            )

    request.session.pop("editing_level_id", None)
    request.session.pop("auto_saved_level_id", None)
    request.session.pop("editing_item_id", None)
    request.session.pop("item_edit_mode", None)
    request.session.pop("editing_item_section", None)
    request.session.pop("new_level", None)
    request.session.pop("item_creation_return_to", None)
    request.session.pop("reset_item_draft_on_create_level3", None)
    request.session.modified = True

    print("Systemnachrichten gespeichert:")
    print(json.dumps(game_json, ensure_ascii=False, indent=2))
    return redirect("level")


@require_POST
def delete_level_view(request, level_id):
    game_json = request.session.get("game_json", {})

    levels = game_json.get("level", [])

    if isinstance(levels, list):
        referencing_levels = referencing_level_ids(levels, level_id)
        if referencing_levels:
            names = ", ".join(str(name) for name in referencing_levels)
            request.session["level_error"] = (
                f'Ein Ausgang in Level {names} verweist noch auf "{level_id}". '
                "Ändere zuerst den Ausgang."
            )
            return redirect("level")

    if isinstance(levels, list):
        game_json["level"] = remove_level_from_list(levels, level_id)

    request.session["game_json"] = game_json
    import_sources = request.session.get("import_sources", {})
    import_sources.pop(str(level_id), None)
    request.session["import_sources"] = import_sources
    database.remove_editor_level_rows(
        request,
        level_id,
    )

    if request.session.get("editing_level_id") == level_id:
        database.discard_editor_level_rows(request, request.session.get("new_level"))
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


def auswahl3(request):
    return render(
        request,
        "editor/auswahl3.html",
    )
def auswahl3v2(request):
    return render(
        request,
        "editor/auswahl3v2.html"
    )


def createlevel1agent(request):
    return render(
        request,
        "editor/createlevel1agent.html",
    )
def createlevel1agentv2(request):
    return render(
        request,
        "editor/createlevel1agentv2.html",
    )

def plugintest1(request):
    return render(
        request,
        "editor/plugintest1.html",
    )

def plugintest2(request):
    return render(
        request, "editor/plugintest2.html"
    )


def figma_overview_45_1891_view(request):
    return render(
        request,
        "editor/figma_overview_45_1891.html",
    )


def figma_levelauswahl_575_2535_view(request):
    return render(
        request,
        "editor/figma_levelauswahl_575_2535.html",
        {
            "steps": [
                {"number": number, "active": number == 1}
                for number in range(1, 9)
            ],
        },
    )


def createlevel1sdd(request):
    return render(
        request,
        "editor/createLevel1sdd.html",
        {
            "steps": get_steps(active_step=1),
        },
    )


def auswahlsdd(request):
    return render(request, "editor/auswahlsdd.html")
