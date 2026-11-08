import sqlite3

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render

from ..services.game_export import build_game_export
from ..services.game_import import GameImportError, import_game
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
    try:
        game_json = import_game(request, uploaded_entries)
    except GameImportError as error:
        return render(request, "editor/start.html", {"error": str(error)})

    clear_editor_state(request)
    request.session["game_json"] = game_json

    request.session.modified = True
    return redirect(
        "level"
    )


def export_game_view(request):
    try:
        archive_bytes = build_game_export(request, settings.BASE_DIR)
        response = HttpResponse(
            archive_bytes,
            content_type="application/zip",
        )
        response["Content-Disposition"] = (
            'attachment; filename="SQLSpellQuest_export.zip"'
        )
        return response
    except (OSError, sqlite3.Error, ValueError) as error:
        game_json = request.session.get("game_json", {})
        levels = game_json.get("level", []) if isinstance(game_json, dict) else []
        return render(request, "editor/level.html", {
            "levels": levels if isinstance(levels, list) else [],
            "error_message": f"Export fehlgeschlagen: {error}",
        }, status=400)
