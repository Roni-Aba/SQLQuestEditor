from copy import deepcopy

from django.shortcuts import redirect, render

from .. import database
from ..services.game_messages import DEFAULT_MESSAGES
from .shared import clear_editor_state, set_guided_level_creation


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
