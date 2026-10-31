import io
import json
import shutil
import sqlite3
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .. import database, utils
from ..services.game_export import (
    write_level_databases,
    write_prepared_assets,
    write_imported_files,
)
from ..services.game_import import (
    select_game_json_entry,
    copy_uploaded_files,
    build_import_sources,
    build_import_manifest,
)
from ..services.game_messages import normalize_game_messages
from .shared import clear_editor_state


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
