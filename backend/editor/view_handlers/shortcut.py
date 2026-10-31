import json
from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect, render

from .. import database, utils
from ..services.game_messages import (
    normalize_game_messages,
    messages_form_values,
    messages_from_post,
)
from ..services.level_basics import (
    level1_form_values,
    level2_form_values,
    query_restriction_from_post,
)
from .shared import (
    current_level_origin_id,
    level_name_is_taken,
    set_guided_level_creation,
)


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
