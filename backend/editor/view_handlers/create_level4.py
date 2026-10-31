import json

from django.shortcuts import redirect, render

from .. import utils
from ..services.item_draft import (
    clear_item_draft,
    has_item_name_conflict,
    parse_unlocked_item,
    set_item_name_and_sync_table,
    set_item_requirements,
)
from .shared import get_steps

def create_level4_view(request):
    steps = get_steps(active_step=4)
    saved_level = request.session.get("new_level", {})

    if not isinstance(saved_level, dict):
        saved_level = {}

    if request.method == "GET":
        return_to = request.GET.get("return_to", "")
        reset_item_draft = request.session.pop(
            "reset_item_draft_on_create_level3",
            False,
        )

        if return_to == "items":
            request.session["item_creation_return_to"] = "items"
            clear_item_draft(saved_level)

            request.session.pop("editing_item_id", None)
            request.session.pop("item_edit_mode", None)
            request.session.pop("editing_item_section", None)

            request.session["new_level"] = saved_level
            request.session.modified = True

        elif return_to == "summary":
            request.session["item_creation_return_to"] = "summary"
            request.session.modified = True

        elif (
            reset_item_draft
            and not request.session.get("item_edit_mode", False)
        ):
            clear_item_draft(saved_level)

            request.session["new_level"] = saved_level
            request.session.modified = True

        elif (
            not request.session.get("item_edit_mode", False)
            and request.session.get("item_creation_return_to")
            not in {"items", "summary", "level8"}
        ):
            request.session.pop("item_creation_return_to", None)
            request.session.modified = True

    return_to_item_overview = (
        request.session.get("item_creation_return_to") == "items"
    )
    return_to_item_summary = (
        request.session.get("item_creation_return_to") == "summary"
    )

    item = saved_level.get("item", {})
    if not isinstance(item, dict):
        item = {}

    if return_to_item_overview:
        back_url_name = "gegenstandVerwaltung"
    else:
        back_urls = {
            "table": "create_level3table",
            "hint": "create_level3hint",
            "exit": "create_level3exit",
        }
        back_url_name = back_urls.get(
            item.get("type", ""),
            "create_level3",
        )

    unlocked_items = item.get("unlockedItems", [])
    if not isinstance(unlocked_items, list):
        unlocked_items = []

    form_values = {
        "item_name": item.get("id", ""),
        "unlocked_items_json": json.dumps(
            unlocked_items,
            ensure_ascii=False,
        ),
    }

    item_options = utils.get_item_options_for_current_level(saved_level)
    error_message = ""
    if request.method == "POST":
        item_name = request.POST.get("item_name", "").strip()
        unlocked_items = parse_unlocked_item(
            request.POST.get("unlocked_items", "[]")
        )
        editing_item_id = request.session.get("editing_item_id", "")
        name_conflict = has_item_name_conflict(saved_level, item, item_name, editing_item_id)
        if name_conflict:
            error_message = (
                f'Der Gegenstands- oder Tabellenname "{item_name}" '
                "wird in diesem Level bereits verwendet."
            )
            form_values["item_name"] = item_name
        else:
            set_item_name_and_sync_table(request, saved_level, item, item_name)
            set_item_requirements(saved_level, item, unlocked_items)

            saved_level["item"] = item
            request.session["new_level"] = saved_level
            request.session.modified = True

            if return_to_item_summary:
                request.session.pop("item_creation_return_to", None)
                request.session.modified = True
                return redirect("create_level7")

            if request.session.get("item_edit_mode", False):
                request.session.pop("editing_item_section", None)
                request.session.modified = True
                if editing_item_id:
                    return redirect(
                        "edit_item",
                        item_id=editing_item_id,
                    )

            return redirect("create_level5")

    return render(
        request,
        "editor/createLevel4.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "item_options": item_options,
            "error_message": error_message,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_overview": return_to_item_overview,
            "return_to_item_summary": return_to_item_summary,
            "back_url_name": back_url_name,
        },
    )