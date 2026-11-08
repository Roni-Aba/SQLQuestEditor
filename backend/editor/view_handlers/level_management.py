import json
from copy import deepcopy

from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .. import database
from ..services.item_service import save_current_item_to_new_level
from ..services.level_basics import level_name_is_taken
from ..services.level_delete import referencing_level_ids, remove_level_from_list
from ..services.level_save import (
    build_level_edit_session,
    build_level_for_json,
    save_level_to_game_json,
)
from .shared import (
    current_level_origin_id,
    set_guided_level_creation,
)


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
        saved_level = save_current_item_to_new_level(saved_level)

    level_for_json = build_level_for_json(saved_level)
    level_id = str(level_for_json.get("id", "")).strip()

    if not level_id:
        return redirect("levelGrunddaten")

    editing_level_id = current_level_origin_id(request, saved_level)
    game_json = request.session.get("game_json", {})
    if level_name_is_taken(game_json, level_id, editing_level_id):
        return redirect("levelGrunddaten")

    game_json = save_level_to_game_json(
        request, saved_level, level_for_json, editing_level_id
    )

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
