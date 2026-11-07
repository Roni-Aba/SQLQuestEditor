import json

from django.conf import settings
from django.shortcuts import redirect, render

from .. import database
from ..services.level_basics import (
    level1_form_values,
    level_name_is_taken,
    update_level_basics,
    update_level_picture,
)
from .shared import get_steps, save_new_level_session

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

        update_level_basics(saved_level, level_id, start_dialog)
        database.finalize_editor_level_rows(
            request,
            saved_level,
            level_id,
        )
        update_level_picture(
            saved_level, request.FILES.get("levelPicture"), settings.BASE_DIR
        )
        save_new_level_session(request, saved_level)
        print("createLevel1 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level2")
    return render(request, "editor/createLevel1.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
    })
