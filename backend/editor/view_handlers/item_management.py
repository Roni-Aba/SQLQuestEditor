import json
from copy import deepcopy

from django.shortcuts import redirect, render

from .. import utils
from ..services.item_draft import (
    clear_item_draft,
    remove_item_from_game_levels,
    remove_deleted_table_rows,
)
from ..services.item_edit import (
    find_item,
    load_item_draft,
    preserve_original_item_fields,
    sync_edited_table_rows,
    replace_item_and_update_references,
)
from ..services.item_summary import get_item_summary
from .shared import get_steps, save_new_level_session, set_guided_level_creation


def gegenstand_view(
    request,
):
    set_guided_level_creation(request, False)
    saved_level = request.session.get(
        "new_level",
        {},
    )

    if not isinstance(
        saved_level,
        dict,
    ):
        saved_level = {}

    items = saved_level.get(
        "items",
        [],
    )

    if not isinstance(
        items,
        list,
    ):
        items = []

    clean_saved_level = {
        **saved_level,
        "items": deepcopy(
            items
        ),
    }

    return render(
        request,
        "editor/gegenstandVerwaltung.html",
        {
            "saved_level": clean_saved_level,
            "steps": get_steps(
                active_step=1
            ),
        },
    )


def edit_item_view(request, item_id):
    set_guided_level_creation(request, False)
    saved_level = request.session.get("new_level", {})

    currently_edited_item = request.session.get("editing_item_id")
    if currently_edited_item != item_id:
        selected_item = load_item_draft(request, saved_level, item_id)
        if selected_item is None:
            print(f"Gegenstand '{item_id}' wurde nicht gefunden.")
            return redirect("gegenstandVerwaltung")

        request.session["new_level"] = saved_level
        request.session["editing_item_id"] = item_id
        request.session.modified = True

    summary = get_item_summary(saved_level)

    if request.method == "POST":
        old_item_id = request.session.get("editing_item_id", item_id)
        current_item = utils.build_item_for_json(saved_level)
        items = saved_level.get("items", [])
        original_item = find_item(items, old_item_id)

        preserve_original_item_fields(
            current_item, original_item, saved_level
        )
        sync_edited_table_rows(
            request, saved_level, current_item, original_item
        )
        saved_level["items"] = replace_item_and_update_references(
            items, old_item_id, current_item
        )

        request.session["new_level"] = saved_level
        request.session.modified = True

        if request.session.get("editing_level_id"):
            game_json = request.session.get("game_json", {})
        else:
            game_json, saved_level = utils.save_new_level_to_game_json(request)

        clear_item_draft(saved_level)
        request.session["new_level"] = saved_level
        request.session["game_json"] = game_json

        request.session.pop("item_edit_mode", None)
        request.session.pop("editing_item_id", None)
        request.session.pop("editing_item_section", None)
        request.session.pop("item_creation_return_to", None)
        request.session.modified = True

        print("Bearbeiteter Gegenstand gespeichert:")
        print(json.dumps(current_item, ensure_ascii=False, indent=2))
        return redirect("gegenstandVerwaltung")

    return render(
        request,
        "editor/editItem.html",
        {
            "saved_level": saved_level,
            "summary": summary,
            "item_id": item_id,
        },
    )


def edit_item_section_view(
        request,
        item_id,
        section,
):
    set_guided_level_creation(request, False)
    allowed_sections = {
        "grunddaten": "create_level4",
        "passwort": "create_level6",
        "position": "create_level51",
        "typ": "create_level31",
        "table": "create_level3table",
        "hint": "create_level3hint",
        "exit": "create_level3exit",
    }
    target_view = allowed_sections.get(
        section
    )
    if target_view is None:
        return redirect(
            "edit_item",
            item_id=item_id,
        )
    request.session.pop(
        "item_creation_return_to",
        None,
    )
    request.session[
        "item_edit_mode"
    ] = True
    request.session[
        "editing_item_id"
    ] = item_id
    request.session[
        "editing_item_section"
    ] = section
    request.session.modified = True
    return redirect(
        target_view
    )


def cancel_item_edit_view(request):
    saved_level = request.session.get("new_level")
    if isinstance(saved_level, dict):
        for draft_key in ("item", "unlockCondition", "position"):
            saved_level.pop(draft_key, None)
        request.session["new_level"] = saved_level

    request.session.pop(
        "item_edit_mode",
        None,
    )
    request.session.pop(
        "editing_item_id",
        None,
    )
    request.session.pop(
        "editing_item_section",
        None,
    )
    request.session.modified = True
    return redirect(
        "gegenstandVerwaltung"
    )


def delete_item_view(request, item_id):
    if request.method != "POST":
        return redirect("gegenstandVerwaltung")

    saved_level = request.session.get("new_level", {})
    level_id = saved_level.get("id", "")

    remove_deleted_table_rows(request, saved_level, item_id)

    saved_level = utils.remove_item_from_level(saved_level, item_id)
    save_new_level_session(request, saved_level)

    game_json = request.session.get("game_json", {})
    levels = game_json.get("level", [])

    if isinstance(levels, list) and level_id:
        game_json["level"] = remove_item_from_game_levels(
            levels,
            level_id,
            item_id,
        )
        request.session["game_json"] = game_json

    if request.session.get("editing_item_id") == item_id:
        request.session.pop("item_edit_mode", None)
        request.session.pop("editing_item_id", None)
        request.session.pop("editing_item_section", None)

    request.session.modified = True
    print("Systemnachrichten gespeichert:")
    print(json.dumps(game_json, ensure_ascii=False, indent=2))
    return redirect("gegenstandVerwaltung")
