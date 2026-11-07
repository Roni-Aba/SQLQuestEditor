import json

from django.conf import settings
from django.shortcuts import redirect, render

from .. import database
from ..services.game_messages import (
    normalize_game_messages,
    messages_form_values,
    messages_from_post,
)
from ..services.level_basics import (
    level1_form_values,
    level2_form_values,
    query_restriction_from_post,
    level_name_is_taken,
    update_level_basics,
    update_level_picture,
)
from .shared import (
    current_level_origin_id,
    set_guided_level_creation,
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

        update_level_picture(
            saved_level, request.FILES.get("levelPicture"), settings.BASE_DIR
        )
        update_level_basics(saved_level, level_name, level_greeting)

        if not request.session.get("editing_level_id"):
            database.finalize_editor_level_rows(
                request,
                saved_level,
                level_name,
            )

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
