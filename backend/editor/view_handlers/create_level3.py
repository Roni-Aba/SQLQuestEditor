from django.shortcuts import redirect, render

from ..services.item_draft import (
    clear_item_draft,
    clear_table_data_on_type_change,
    item_type_and_next_view,
)
from .shared import get_steps, remember_item_summary_return


def create_level3_view(request):
    steps = get_steps(active_step=3)
    saved_level = request.session.get("new_level", {})

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

    return_to_item_summary = (
        request.session.get("item_creation_return_to") == "summary"
    )
    return_to_item_overview = (
        request.session.get("item_creation_return_to") == "items"
    )
    return_to_level8 = (
        request.session.get("item_creation_return_to") == "level8"
    )
    item = saved_level.get("item", {})
    form_values = {"item_type": item.get("type", "")}

    if request.method == "POST":
        return redirect("create_level31")

    return render(
        request,
        "editor/createLevel3.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_overview": return_to_item_overview,
            "return_to_item_summary": return_to_item_summary,
            "return_to_level8": return_to_level8,
        },
    )


def create_level31_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    return_to_item_overview = (
        request.session.get("item_creation_return_to") == "items"
    )
    steps = get_steps(active_step=3)
    saved_level = request.session.get("new_level", {})
    item = saved_level.get("item", {})

    type_options = [
        {"value": "table", "label": "Table"},
        {"value": "hint", "label": "Hint"},
        {"value": "exit", "label": "Exit"},
    ]
    form_values = {"item_type": item.get("type", "")}

    if request.method == "POST":
        item_type, next_view = item_type_and_next_view(request.POST)
        clear_table_data_on_type_change(
            request,
            saved_level,
            item,
            item_type,
        )

        item["type"] = item_type
        saved_level["item"] = item
        request.session["new_level"] = saved_level
        request.session.modified = True

        return redirect(next_view)

    return render(
        request,
        "editor/createLevel3-1.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "type_options": type_options,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_overview": return_to_item_overview,
            "return_to_item_summary": return_to_item_summary,
        },
    )