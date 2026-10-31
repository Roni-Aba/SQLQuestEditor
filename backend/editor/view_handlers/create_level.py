from django.shortcuts import render

from .. import database
from .shared import get_steps, set_guided_level_creation


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
