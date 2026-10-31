from . import database, utils
from copy import deepcopy
import json, io, zipfile, sqlite3, tempfile, shutil
from pathlib import Path, PurePosixPath
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render

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

from .services.game_messages import (
    DEFAULT_MESSAGES,
    normalize_game_messages,
)

from .view_handlers.shared import (
    set_guided_level_creation,
    redirect_after_item_section_edit,
)

from .view_handlers.create_level import create_level
from .view_handlers.create_level1 import create_level1_view
from .view_handlers.create_level2 import create_level2_view
from .view_handlers.create_level3 import (
    create_level3_view,
    create_level31_view,
    create_level3exit_view,
    create_level3hint_view,
    create_level3table_view,
)

from .view_handlers.create_level4 import (
    create_level4_view,
)
from .view_handlers.create_level5 import (
    create_level5_view,
    create_level51_view,
)
from .view_handlers.create_level6 import (
    create_level6_view,
    create_level61_view,
    create_level62_view,
)
from .view_handlers.create_level7 import create_level7_view
from .view_handlers.create_level8 import create_level8_view
from .view_handlers.shortcut import (
    level_grunddaten_view,
    sql_grunddaten_view,
    messages_grunddaten_view,
)
from .view_handlers.level_management import (
    level_view,
    edit_level_view,
    save_level_view,
    delete_level_view,
)
from .view_handlers.item_management import (
    gegenstand_view,
    edit_item_view,
    edit_item_section_view,
    cancel_item_edit_view,
    delete_item_view,
)
from .view_handlers.testingScratchView import (
    auswahl3,
    auswahl3v2,
    createlevel1agent,
    createlevel1agentv2,
    plugintest1,
    plugintest2,
    figma_overview_45_1891_view,
    figma_levelauswahl_575_2535_view,
    createlevel1sdd,
    auswahlsdd,
)


def first_or_empty(values):
    return values[0] if values else ""


def parse_optional_int(value):
    value = str(value).strip()
    if value.isdigit():
        return int(value)
    return None


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
