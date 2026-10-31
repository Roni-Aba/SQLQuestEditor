import json

from django.shortcuts import redirect, render

from .. import utils
from ..services.item_draft import clear_item_draft
from .shared import get_steps


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
